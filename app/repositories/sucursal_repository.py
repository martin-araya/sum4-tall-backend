from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sucursal import Sucursal
from app.repositories.base import BaseRepository
from app.schemas.sucursal import SucursalCreate, SucursalUpdate


class SucursalRepository(BaseRepository[Sucursal, SucursalCreate, SucursalUpdate]):
    model = Sucursal

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_region(
        self, region: str, page: int = 1, size: int = 20
    ) -> tuple[list[Sucursal], int]:
        offset = (page - 1) * size
        where = Sucursal.region == region

        count_result = await self.session.execute(
            select(func.count()).select_from(Sucursal).where(where)
        )
        total = count_result.scalar_one()

        items_result = await self.session.execute(
            select(Sucursal).where(where).offset(offset).limit(size)
        )
        return list(items_result.scalars().all()), total

    async def get_activas(
        self, page: int = 1, size: int = 20
    ) -> tuple[list[Sucursal], int]:
        offset = (page - 1) * size
        where = Sucursal.activo.is_(True)

        count_result = await self.session.execute(
            select(func.count()).select_from(Sucursal).where(where)
        )
        total = count_result.scalar_one()

        items_result = await self.session.execute(
            select(Sucursal).where(where).offset(offset).limit(size)
        )
        return list(items_result.scalars().all()), total
