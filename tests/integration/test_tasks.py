import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.auditor import Auditor
from app.models.auditoria import Auditoria
from app.models.sucursal import Sucursal
from app.models.usuario import Usuario
import app.workers.tasks
from app.workers.tasks import calculate_sucursal_average_score


async def test_calculate_sucursal_average_score_task(
    db: AsyncSession, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    # 1. Crear Sucursal
    sucursal = Sucursal(
        nombre="Sucursal Para Promediar",
        region="Biobío",
        direccion="Av. Universidad 456",
        puntaje_promedio=None,
    )
    db.add(sucursal)
    await db.commit()
    await db.refresh(sucursal)

    # 2. Crear Usuario y Auditor
    user = Usuario(
        nombre="Auditor de Tarea",
        email="task_auditor@test.com",
        password_hash="fakehash",
        rol="auditor",
        activo=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    auditor = Auditor(
        usuario_id=user.id,
        nombre=user.nombre,
        email=user.email,
        region="Biobío",
        activo=True,
    )
    db.add(auditor)
    await db.commit()
    await db.refresh(auditor)

    # 3. Crear auditorías con puntajes con fechas programadas válidas
    now = datetime.now(timezone.utc)
    auditoria1 = Auditoria(
        sucursal_id=sucursal.id,
        auditor_id=auditor.id,
        estado="completada",
        puntaje=80.0,
        fecha_programada=now,
    )
    auditoria2 = Auditoria(
        sucursal_id=sucursal.id,
        auditor_id=auditor.id,
        estado="con_observaciones",
        puntaje=90.0,
        fecha_programada=now,
    )
    # Auditoría programada (no cuenta para el promedio)
    auditoria3 = Auditoria(
        sucursal_id=sucursal.id,
        auditor_id=auditor.id,
        estado="programada",
        puntaje=50.0,
        fecha_programada=now,
    )
    db.add_all([auditoria1, auditoria2, auditoria3])
    await db.commit()

    # 4. Correr la tarea de cálculo sobreescribiendo el session_factory de la tarea
    # para usar la conexión de prueba en SQLite
    original_factory = app.workers.tasks.async_session_factory
    app.workers.tasks.async_session_factory = session_factory
    try:
        avg_score = await calculate_sucursal_average_score({}, str(sucursal.id))
    finally:
        app.workers.tasks.async_session_factory = original_factory

    # Promedio esperado de (80 + 90) / 2 = 85.0
    assert avg_score == 85.0

    # 5. Verificar que la sucursal se haya actualizado en base de datos
    await db.refresh(sucursal)
    assert float(sucursal.puntaje_promedio) == 85.0
