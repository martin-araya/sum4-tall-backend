from collections.abc import AsyncGenerator
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

_settings = get_settings()
logger = logging.getLogger("auditchain.database")

engine: AsyncEngine = create_async_engine(
    _settings.database_url,
    echo=_settings.environment == "development",
    pool_pre_ping=True,
)

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        # Mask password for safe logging
        safe_url = _settings.database_url
        try:
            if "@" in safe_url:
                parts = safe_url.split("@")
                creds = parts[0].split(":")
                if len(creds) > 2:
                    safe_url = f"{creds[0]}:{creds[1]}:******@{parts[1]}"
        except Exception:
            pass
            
        logger.exception("Database connection verification failed for %s: %s", safe_url, str(e))
        return False
