import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import DomainError, NotFound, PermissionDenied
from app.models.auditor import Auditor
from app.models.auditoria import Auditoria
from app.models.usuario import Usuario
from app.repositories.auditor_repository import AuditorRepository
from app.repositories.auditoria_repository import AuditoriaRepository
from app.repositories.sucursal_repository import SucursalRepository
from app.schemas.auditoria import AuditoriaCreate, AuditoriaOut, AuditoriaUpdate
from app.schemas.common import PaginatedResponse

VALID_TRANSITIONS: dict[str, set[str]] = {
    "pendiente": {"completada", "con_observaciones", "vencida"},
    "completada": set(),
    "con_observaciones": set(),
    "vencida": set(),
}


def _to_out(auditoria: Auditoria) -> AuditoriaOut:
    return AuditoriaOut(
        id=auditoria.id,
        sucursal_id=auditoria.sucursal_id,
        auditor_id=auditoria.auditor_id,
        fecha_programada=auditoria.fecha_programada,
        observaciones=auditoria.observaciones,
        estado=auditoria.estado,
        puntaje=float(auditoria.puntaje) if auditoria.puntaje is not None else None,
        sucursal_nombre=auditoria.sucursal.nombre if auditoria.sucursal else "",
        auditor_nombre=auditoria.auditor.usuario.nombre
        if auditoria.auditor and auditoria.auditor.usuario
        else "",
        fecha_realizada=auditoria.fecha_realizada,
        creado_en=auditoria.creado_en,
    )


async def get_all(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    estado: str | None = None,
    sucursal_id: uuid.UUID | None = None,
) -> PaginatedResponse[AuditoriaOut]:
    offset = (page - 1) * size

    base = select(Auditoria)
    count_base = select(func.count()).select_from(Auditoria)

    if estado is not None:
        base = base.where(Auditoria.estado == estado)
        count_base = count_base.where(Auditoria.estado == estado)

    if sucursal_id is not None:
        base = base.where(Auditoria.sucursal_id == sucursal_id)
        count_base = count_base.where(Auditoria.sucursal_id == sucursal_id)

    count_result = await db.execute(count_base)
    total = count_result.scalar_one()

    items_result = await db.execute(
        base.options(
            selectinload(Auditoria.sucursal),
            selectinload(Auditoria.auditor).selectinload(Auditor.usuario),
        )
        .order_by(Auditoria.creado_en.desc())
        .offset(offset)
        .limit(size)
    )
    items = list(items_result.scalars().all())

    return PaginatedResponse[AuditoriaOut].build(
        items=[_to_out(a) for a in items],
        total=total,
        page=page,
        size=size,
    )


async def get_by_id(db: AsyncSession, id: uuid.UUID) -> AuditoriaOut:
    result = await db.execute(
        select(Auditoria)
        .where(Auditoria.id == id)
        .options(
            selectinload(Auditoria.sucursal),
            selectinload(Auditoria.auditor).selectinload(Auditor.usuario),
        )
    )
    auditoria = result.scalar_one_or_none()
    if auditoria is None:
        raise NotFound(f"Auditoría {id} no encontrada")
    return _to_out(auditoria)


async def create(
    db: AsyncSession, schema: AuditoriaCreate, current_user: Usuario
) -> AuditoriaOut:
    sucursal_repo = SucursalRepository(db)
    auditor_repo = AuditorRepository(db)

    sucursal = await sucursal_repo.get(schema.sucursal_id)
    if sucursal is None or not sucursal.activo:
        raise DomainError("Sucursal no encontrada o inactiva")

    auditor = await auditor_repo.get(schema.auditor_id)
    if auditor is None or not auditor.activo:
        raise DomainError("Auditor no encontrado o inactivo")

    if current_user.rol == "auditor":
        own_auditor = await auditor_repo.get_by_usuario_id(current_user.id)
        if own_auditor is None or own_auditor.id != schema.auditor_id:
            raise PermissionDenied(
                "Un auditor solo puede crear auditorías con su propio auditor_id"
            )

    from datetime import datetime, timezone
    
    estado = "pendiente"
    fecha_realizada = None
    if schema.puntaje is not None:
        fecha_realizada = datetime.now(timezone.utc)
        estado = "completada" if schema.puntaje >= 75 else "con_observaciones"

    auditoria = Auditoria(
        sucursal_id=schema.sucursal_id,
        auditor_id=schema.auditor_id,
        fecha_programada=schema.fecha_programada,
        observaciones=schema.observaciones,
        puntaje=schema.puntaje,
        estado=estado,
        fecha_realizada=fecha_realizada,
    )
    db.add(auditoria)
    await db.flush()

    return await get_by_id(db, auditoria.id)


async def update(
    db: AsyncSession,
    id: uuid.UUID,
    schema: AuditoriaUpdate,
    current_user: Usuario,
) -> AuditoriaOut:
    repo = AuditoriaRepository(db)
    auditoria = await repo.get(id)
    if auditoria is None:
        raise NotFound(f"Auditoría {id} no encontrada")

    if schema.estado is not None and schema.estado != auditoria.estado:
        allowed = VALID_TRANSITIONS.get(auditoria.estado, set())
        if schema.estado not in allowed:
            raise DomainError(
                f"Transición de estado inválida: '{auditoria.estado}' → '{schema.estado}'"
            )

    updated = await repo.update(id, schema)
    if updated is None:
        raise NotFound(f"Auditoría {id} no encontrada")

    return await get_by_id(db, updated.id)


async def get_stats(db: AsyncSession) -> dict:
    repo = AuditoriaRepository(db)
    return await repo.get_stats()
