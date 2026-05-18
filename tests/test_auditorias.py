import uuid
from datetime import datetime, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auditor import Auditor
from app.models.sucursal import Sucursal
from app.models.usuario import Usuario


async def test_get_auditorias_empty(client: AsyncClient, token_admin: str) -> None:
    response = await client.get(
        "/api/v1/auditorias/",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] == 0
    assert len(data["items"]) == 0


async def test_create_auditoria_lifecycle(
    client: AsyncClient,
    db: AsyncSession,
    token_admin: str,
    token_auditor: str,
    usuario_auditor: Usuario,
) -> None:
    # 1. Crear Sucursal
    sucursal = Sucursal(
        nombre="Sucursal Test Auditoria",
        region="Valparaíso",
        direccion="Calle de Prueba 123",
    )
    db.add(sucursal)
    await db.commit()
    await db.refresh(sucursal)

    # 2. Instanciar Auditor en la DB usando el usuario auditor de la fixture
    auditor_model = Auditor(
        usuario_id=usuario_auditor.id,
        nombre=usuario_auditor.nombre,
        email=usuario_auditor.email,
        region="Valparaíso",
        activo=True,
    )
    db.add(auditor_model)
    await db.commit()
    await db.refresh(auditor_model)

    # 3. Crear Auditoría (POST)
    payload_create = {
        "sucursal_id": str(sucursal.id),
        "auditor_id": str(auditor_model.id),
        "fecha_programada": datetime.now(timezone.utc).isoformat(),
        "observaciones": "Observación inicial de prueba",
        "puntaje": None,
    }

    response = await client.post(
        "/api/v1/auditorias/",
        json=payload_create,
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert response.status_code == 201
    data_created = response.json()
    assert "id" in data_created
    assert data_created["sucursal_id"] == str(sucursal.id)
    assert data_created["auditor_id"] == str(auditor_model.id)
    assert data_created["estado"] == "pendiente"
    assert data_created["sucursal_nombre"] == sucursal.nombre
    assert data_created["auditor_nombre"] == auditor_model.nombre

    auditoria_id = data_created["id"]

    # 4. Obtener Auditoría por ID (GET)
    response_get = await client.get(
        f"/api/v1/auditorias/{auditoria_id}",
        headers={"Authorization": f"Bearer {token_auditor}"},
    )
    assert response_get.status_code == 200
    assert response_get.json()["id"] == auditoria_id

    # 5. Obtener Estadísticas (GET /stats)
    response_stats = await client.get(
        "/api/v1/auditorias/stats",
        headers={"Authorization": f"Bearer {token_auditor}"},
    )
    assert response_stats.status_code == 200
    stats_data = response_stats.json()
    assert "total" in stats_data
    assert "por_estado" in stats_data
    assert "promedio_general" in stats_data

    # 6. Actualizar Auditoría (PUT)
    payload_update = {
        "estado": "completada",
        "puntaje": 92.5,
        "observaciones": "Auditoría finalizada con excelente puntaje",
        "fecha_realizada": datetime.now(timezone.utc).isoformat(),
    }
    response_update = await client.put(
        f"/api/v1/auditorias/{auditoria_id}",
        json=payload_update,
        headers={"Authorization": f"Bearer {token_auditor}"},
    )
    assert response_update.status_code == 200
    data_updated = response_update.json()
    assert data_updated["estado"] == "completada"
    assert data_updated["puntaje"] == 92.5
    assert data_updated["observaciones"] == "Auditoría finalizada con excelente puntaje"
    assert data_updated["fecha_realizada"] is not None

    # 7. Listar Auditorías con filtros
    response_list = await client.get(
        f"/api/v1/auditorias/?sucursal_id={sucursal.id}&estado=completada",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert response_list.status_code == 200
    list_data = response_list.json()
    assert list_data["total"] == 1
    assert list_data["items"][0]["id"] == auditoria_id
