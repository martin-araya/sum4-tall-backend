import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.auditoria import Auditoria
from app.repositories.base import BaseRepository
from app.schemas.auditoria import AuditoriaCreate, AuditoriaUpdate


class AuditoriaRepository(BaseRepository[Auditoria, AuditoriaCreate, AuditoriaUpdate]):
    model = Auditoria

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_sucursal(
        self, sucursal_id: uuid.UUID, page: int = 1, size: int = 20
    ) -> tuple[list[Auditoria], int]:
        offset = (page - 1) * size
        where = Auditoria.sucursal_id == sucursal_id

        count_result = await self.session.execute(
            select(func.count()).select_from(Auditoria).where(where)
        )
        total = count_result.scalar_one()

        items_result = await self.session.execute(
            select(Auditoria).where(where).order_by(Auditoria.creado_en.desc()).offset(offset).limit(size)
        )
        return list(items_result.scalars().all()), total

    async def get_by_estado(
        self, estado: str, page: int = 1, size: int = 20
    ) -> tuple[list[Auditoria], int]:
        offset = (page - 1) * size
        where = Auditoria.estado == estado

        count_result = await self.session.execute(
            select(func.count()).select_from(Auditoria).where(where)
        )
        total = count_result.scalar_one()

        items_result = await self.session.execute(
            select(Auditoria).where(where).order_by(Auditoria.creado_en.desc()).offset(offset).limit(size)
        )
        return list(items_result.scalars().all()), total

    async def get_with_relations(self, id: uuid.UUID) -> Auditoria | None:
        result = await self.session.execute(
            select(Auditoria)
            .where(Auditoria.id == id)
            .options(
                selectinload(Auditoria.sucursal),
                selectinload(Auditoria.auditor),
            )
        )
        return result.scalar_one_or_none()

    async def get_paginated(
        self, page: int = 1, size: int = 20
    ) -> tuple[list[Auditoria], int]:
        offset = (page - 1) * size

        count_result = await self.session.execute(
            select(func.count()).select_from(Auditoria)
        )
        total = count_result.scalar_one()

        items_result = await self.session.execute(
            select(Auditoria).order_by(Auditoria.creado_en.desc()).offset(offset).limit(size)
        )
        items = list(items_result.scalars().all())

        return items, total

    async def get_stats(self) -> dict:
        total_result = await self.session.execute(
            select(func.count()).select_from(Auditoria)
        )
        total = total_result.scalar_one()

        estados_result = await self.session.execute(
            select(Auditoria.estado, func.count().label("count"))
            .group_by(Auditoria.estado)
        )
        por_estado = {row.estado: row.count for row in estados_result}

        avg_result = await self.session.execute(
            select(func.avg(Auditoria.puntaje)).where(Auditoria.puntaje.is_not(None))
        )
        promedio = avg_result.scalar_one()

        return {
            "total": total,
            "por_estado": por_estado,
            "promedio_general": round(float(promedio), 2) if promedio is not None else 0.0,
        }
