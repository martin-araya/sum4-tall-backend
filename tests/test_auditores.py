import uuid
from httpx import AsyncClient
from app.models.usuario import Usuario

async def test_get_auditores(client: AsyncClient, token_admin: str) -> None:
    response = await client.get(
        "/api/v1/auditores/",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert response.status_code == 200

async def test_create_auditor(client: AsyncClient, token_admin: str, usuario_auditor: Usuario) -> None:
    payload = {
        "usuario_id": str(usuario_auditor.id),
        "nombre": "Valentina Lagos",
        "email": "valentina.lagos@auditchain.cl",
        "region": "Valparaíso"
    }
    response = await client.post(
        "/api/v1/auditores/",
        json=payload,
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert response.status_code == 201

async def test_get_auditor_by_id(client: AsyncClient, token_admin: str, usuario_auditor: Usuario) -> None:
    payload = {
        "usuario_id": str(usuario_auditor.id),
        "nombre": "Valentina Lagos",
        "email": "valentina.lagos@auditchain.cl",
        "region": "Valparaíso"
    }
    create_resp = await client.post(
        "/api/v1/auditores/",
        json=payload,
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert create_resp.status_code == 201
    auditor_id = create_resp.json()["id"]

    get_resp = await client.get(
        f"/api/v1/auditores/{auditor_id}",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert get_resp.status_code == 200
