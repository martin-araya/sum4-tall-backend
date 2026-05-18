import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import Conflict, DomainError, NotFound
from app.models.auditor import Auditor
from app.repositories.auditor_repository import AuditorRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auditor import AuditorCreate, AuditorOut, AuditorUpdate
from app.schemas.common import PaginatedResponse


async def get_all(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    activos_only: bool = False,
) -> PaginatedResponse[AuditorOut]:
    repo = AuditorRepository(db)

    if activos_only:
        items, total = await repo.get_activos(page=page, size=size)
    else:
        items, total = await repo.get_paginated(page=page, size=size)

    return PaginatedResponse[AuditorOut].build(
        items=[AuditorOut.model_validate(a) for a in items],
        total=total,
        page=page,
        size=size,
    )


async def get_by_id(db: AsyncSession, id: uuid.UUID) -> AuditorOut:
    repo = AuditorRepository(db)
    auditor = await repo.get(id)
    if auditor is None:
        raise NotFound(f"Auditor {id} no encontrado")
    return AuditorOut.model_validate(auditor)


async def create(db: AsyncSession, schema: AuditorCreate) -> AuditorOut:
    auditor_repo = AuditorRepository(db)
    usuario_repo = UsuarioRepository(db)

    usuario = await usuario_repo.get(schema.usuario_id)
    if usuario is None:
        raise DomainError(f"Usuario {schema.usuario_id} no encontrado")
    if usuario.rol != "auditor":
        raise DomainError("El usuario referenciado debe tener rol='auditor'")
    if not usuario.activo:
        raise DomainError("El usuario referenciado está inactivo")

    existing = await auditor_repo.get_by_usuario_id(schema.usuario_id)
    if existing is not None:
        raise Conflict(f"Ya existe un auditor para el usuario {schema.usuario_id}")

    auditor = Auditor(
        usuario_id=schema.usuario_id,
        nombre=schema.nombre,
        email=schema.email,
        region=schema.region,
    )
    db.add(auditor)
    await db.flush()
    await db.refresh(auditor)

    return AuditorOut.model_validate(auditor)


async def update(
    db: AsyncSession, id: uuid.UUID, schema: AuditorUpdate
) -> AuditorOut:
    repo = AuditorRepository(db)
    auditor = await repo.update(id, schema)
    if auditor is None:
        raise NotFound(f"Auditor {id} no encontrado")
    return AuditorOut.model_validate(auditor)


async def delete(db: AsyncSession, id: uuid.UUID) -> None:
    repo = AuditorRepository(db)
    ok = await repo.delete(id)
    if not ok:
        raise NotFound(f"Auditor {id} no encontrado")
