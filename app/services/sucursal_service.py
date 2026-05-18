import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFound
from app.repositories.sucursal_repository import SucursalRepository
from app.schemas.common import PaginatedResponse
from app.schemas.sucursal import SucursalCreate, SucursalOut, SucursalUpdate


async def get_all(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    region: str | None = None,
    activas_only: bool = False,
) -> PaginatedResponse[SucursalOut]:
    repo = SucursalRepository(db)

    if region is not None:
        items, total = await repo.get_by_region(region, page=page, size=size)
    elif activas_only:
        items, total = await repo.get_activas(page=page, size=size)
    else:
        items, total = await repo.get_paginated(page=page, size=size)

    return PaginatedResponse[SucursalOut].build(
        items=[SucursalOut.model_validate(s) for s in items],
        total=total,
        page=page,
        size=size,
    )


async def get_by_id(db: AsyncSession, id: uuid.UUID) -> SucursalOut:
    repo = SucursalRepository(db)
    sucursal = await repo.get(id)
    if sucursal is None:
        raise NotFound(f"Sucursal {id} no encontrada")
    return SucursalOut.model_validate(sucursal)


async def create(db: AsyncSession, schema: SucursalCreate) -> SucursalOut:
    repo = SucursalRepository(db)
    sucursal = await repo.create(schema)
    return SucursalOut.model_validate(sucursal)


async def update(
    db: AsyncSession, id: uuid.UUID, schema: SucursalUpdate
) -> SucursalOut:
    repo = SucursalRepository(db)
    sucursal = await repo.update(id, schema)
    if sucursal is None:
        raise NotFound(f"Sucursal {id} no encontrada")
    return SucursalOut.model_validate(sucursal)
