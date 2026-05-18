import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import Conflict, DomainError, NotFound
from app.core.security import get_password_hash
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.common import PaginatedResponse
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate


async def get_all(
    db: AsyncSession, page: int = 1, size: int = 20
) -> PaginatedResponse[UsuarioOut]:
    repo = UsuarioRepository(db)
    items, total = await repo.get_paginated(page=page, size=size)
    return PaginatedResponse[UsuarioOut].build(
        items=[UsuarioOut.model_validate(u) for u in items],
        total=total,
        page=page,
        size=size,
    )


async def get_by_id(db: AsyncSession, id: uuid.UUID) -> UsuarioOut:
    repo = UsuarioRepository(db)
    user = await repo.get(id)
    if user is None:
        raise NotFound(f"Usuario {id} no encontrado")
    return UsuarioOut.model_validate(user)


async def create(db: AsyncSession, schema: UsuarioCreate) -> UsuarioOut:
    repo = UsuarioRepository(db)

    if schema.rol not in {"admin", "auditor"}:
        raise DomainError("rol debe ser 'admin' o 'auditor'")

    existing = await repo.get_by_email(schema.email)
    if existing is not None:
        raise Conflict(f"Ya existe un usuario con email {schema.email}")

    user = Usuario(
        nombre=schema.nombre,
        email=schema.email,
        rol=schema.rol,
        password_hash=get_password_hash(schema.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    if schema.rol == "auditor":
        from app.models.auditor import Auditor
        auditor = Auditor(
            usuario_id=user.id,
            nombre=user.nombre,
            email=user.email,
            region="No asignada"
        )
        db.add(auditor)
        await db.flush()

    return UsuarioOut.model_validate(user)


async def update(
    db: AsyncSession, id: uuid.UUID, schema: UsuarioUpdate
) -> UsuarioOut:
    repo = UsuarioRepository(db)
    user = await repo.get(id)
    if user is None:
        raise NotFound(f"Usuario {id} no encontrado")

    data = schema.model_dump(exclude_unset=True)

    if "email" in data and data["email"] != user.email:
        existing = await repo.get_by_email(data["email"])
        if existing is not None:
            raise Conflict(f"Ya existe un usuario con email {data['email']}")

    for field, value in data.items():
        setattr(user, field, value)

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return UsuarioOut.model_validate(user)


async def delete(db: AsyncSession, id: uuid.UUID) -> None:
    repo = UsuarioRepository(db)
    ok = await repo.delete(id)
    if not ok:
        raise NotFound(f"Usuario {id} no encontrado")
