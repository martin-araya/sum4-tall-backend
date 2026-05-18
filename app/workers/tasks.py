import asyncio
import uuid
import structlog
from arq.connections import RedisSettings
from sqlalchemy import func, select
from decimal import Decimal

from app.core.config import get_settings
from app.core.database import async_session_factory
from app.models.auditoria import Auditoria
from app.models.sucursal import Sucursal

logger = structlog.get_logger("auditchain.worker")


async def calculate_sucursal_average_score(ctx: dict, sucursal_id: str) -> float | None:
    """Recalcula asíncronamente el puntaje promedio de una sucursal basándose en
    sus auditorías completadas.
    """
    # Manejar conversión de UUID en formato string o UUID object para compatibilidad con SQLite
    sucursal_uuid = uuid.UUID(sucursal_id) if isinstance(sucursal_id, str) else sucursal_id

    logger.info("worker.calculate_sucursal_average_score.start", sucursal_id=sucursal_id)

    async with async_session_factory() as db:
        try:
            # 1. Calcular promedio de auditorías
            stmt = select(func.avg(Auditoria.puntaje)).where(
                Auditoria.sucursal_id == sucursal_uuid,
                Auditoria.estado.in_(["completada", "con_observaciones"]),
                Auditoria.puntaje.is_not(None),
            )
            result = await db.execute(stmt)
            average = result.scalar()

            # 2. Obtener y actualizar la sucursal
            stmt_update = select(Sucursal).where(Sucursal.id == sucursal_uuid)
            sucursal_result = await db.execute(stmt_update)
            sucursal = sucursal_result.scalar_one_or_none()

            if sucursal:
                # Convertir a Decimal para que sea asignable a la propiedad mapped_column de SQLAlchemy
                sucursal.puntaje_promedio = Decimal(str(average)) if average is not None else Decimal("0")
                db.add(sucursal)
                await db.commit()
                logger.info(
                    "worker.calculate_sucursal_average_score.success",
                    sucursal_id=sucursal_id,
                    average=float(average) if average is not None else None,
                )
                return float(average) if average is not None else None
            else:
                logger.warning(
                    "worker.calculate_sucursal_average_score.not_found",
                    sucursal_id=sucursal_id,
                )
                return None
        except Exception as e:
            await db.rollback()
            logger.exception(
                "worker.calculate_sucursal_average_score.failed",
                sucursal_id=sucursal_id,
                error=str(e),
            )
            raise


async def send_notification_email(
    ctx: dict, recipient: str, subject: str, body: str
) -> bool:
    """Simula el envío de una notificación por correo electrónico en segundo plano."""
    logger.info("worker.send_notification_email.start", recipient=recipient, subject=subject)
    try:
        # Simular I/O
        await asyncio.sleep(1.0)
        logger.info("worker.send_notification_email.success", recipient=recipient)
        return True
    except Exception as e:
        logger.exception(
            "worker.send_notification_email.failed", recipient=recipient, error=str(e)
        )
        return False


# Ciclo de vida del worker
async def startup(ctx: dict) -> None:
    logger.info("worker.startup")


async def shutdown(ctx: dict) -> None:
    logger.info("worker.shutdown")


# Configuración del worker requerida por arq CLI
class WorkerSettings:
    functions = [calculate_sucursal_average_score, send_notification_email]
    on_startup = startup
    on_shutdown = shutdown

    settings = get_settings()
    # Conexión a Redis según el entorno
    redis_settings = RedisSettings(
        host="redis" if settings.environment == "production" else "localhost",
        port=6379,
    )
