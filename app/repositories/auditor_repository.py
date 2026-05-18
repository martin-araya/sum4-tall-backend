import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.auditor import Auditor
from app.repositories.base import BaseRepository
from app.schemas.auditor import AuditorCreate, AuditorUpdate


class AuditorRepository(BaseRepository[Auditor, AuditorCreate, AuditorUpdate]):
    model = Auditor

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_usuario_id(self, usuario_id: uuid.UUID) -> Auditor | None:
        result = await self.session.execute(
            select(Auditor).where(Auditor.usuario_id == usuario_id)
        )
        return result.scalar_one_or_none()

    async def get_activos(
        self, page: int = 1, size: int = 20
    ) -> tuple[list[Auditor], int]:
        offset = (page - 1) * size
        where = Auditor.activo.is_(True)

        count_result = await self.session.execute(
            select(func.count()).select_from(Auditor).where(where)
        )
        total = count_result.scalar_one()

        items_result = await self.session.execute(
            select(Auditor).where(where).offset(offset).limit(size)
        )
        return list(items_result.scalars().all()), total

    async def get_with_usuario(self, id: uuid.UUID) -> Auditor | None:
        result = await self.session.execute(
            select(Auditor)
            .where(Auditor.id == id)
            .options(selectinload(Auditor.usuario))
        )
        return result.scalar_one_or_none()
