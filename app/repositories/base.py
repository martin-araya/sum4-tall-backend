import uuid
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchema, UpdateSchema]):
    model: type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id: uuid.UUID) -> ModelType | None:
        return await self.session.get(self.model, id)

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[ModelType]:
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_paginated(
        self, page: int = 1, size: int = 20
    ) -> tuple[list[ModelType], int]:
        offset = (page - 1) * size

        count_result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        total = count_result.scalar_one()

        items_result = await self.session.execute(
            select(self.model).offset(offset).limit(size)
        )
        items = list(items_result.scalars().all())

        return items, total

    async def create(self, schema: CreateSchema) -> ModelType:
        data = schema.model_dump(exclude_unset=False)
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: uuid.UUID, schema: UpdateSchema) -> ModelType | None:
        instance = await self.get(id)
        if instance is None:
            return None

        data: dict[str, Any] = schema.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(instance, field, value)

        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: uuid.UUID) -> bool:
        instance = await self.get(id)
        if instance is None:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True
