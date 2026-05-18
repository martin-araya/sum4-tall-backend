import os
from collections.abc import AsyncGenerator

# Set env vars BEFORE importing app modules so Settings() validates cleanly.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "dev")
os.environ.setdefault("PUBLIC_KEY", "dev")
os.environ.setdefault("ENVIRONMENT", "development")

import pytest_asyncio  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import event, text  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.api.deps import get_db  # noqa: E402
from app.core.database import Base  # noqa: E402
from app.core.security import create_access_token, get_password_hash  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    # SQLite no tiene schemas — adjuntamos una DB en memoria con nombre 'auditchain'
    # para que las tablas calificadas como auditchain.<tabla> se resuelvan.
    @event.listens_for(engine.sync_engine, "connect")
    def _attach_schema(dbapi_conn, _):
        dbapi_conn.execute("ATTACH DATABASE ':memory:' AS auditchain")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db(session_factory) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def app(session_factory) -> AsyncGenerator[FastAPI, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield fastapi_app
    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def usuario_admin(db: AsyncSession) -> Usuario:
    user = Usuario(
        nombre="Admin Test",
        email="admin@test.com",
        password_hash=get_password_hash("admin123"),
        rol="admin",
        activo=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def usuario_auditor(db: AsyncSession) -> Usuario:
    user = Usuario(
        nombre="Auditor Test",
        email="auditor@test.com",
        password_hash=get_password_hash("auditor123"),
        rol="auditor",
        activo=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def token_admin(usuario_admin: Usuario) -> str:
    return create_access_token({"sub": str(usuario_admin.id), "rol": usuario_admin.rol})


@pytest_asyncio.fixture
async def token_auditor(usuario_auditor: Usuario) -> str:
    return create_access_token({"sub": str(usuario_auditor.id), "rol": usuario_auditor.rol})
