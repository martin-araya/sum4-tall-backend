import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.auditor import Auditor
    from app.models.sucursal import Sucursal


class Auditoria(Base):
    __tablename__ = "auditorias"
    __table_args__ = {"schema": "auditchain"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    sucursal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auditchain.sucursales.id", ondelete="RESTRICT")
    )
    auditor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auditchain.auditores.id", ondelete="RESTRICT")
    )
    fecha_programada: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fecha_realizada: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    puntaje: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    estado: Mapped[str] = mapped_column(
        ENUM("pendiente", "completada", "con_observaciones", "vencida", name="enum_estado_auditoria", schema="auditchain", create_type=False),
        server_default="pendiente"
    )
    observaciones: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    sucursal: Mapped["Sucursal"] = relationship(back_populates="auditorias")
    auditor: Mapped["Auditor"] = relationship(back_populates="auditorias")
