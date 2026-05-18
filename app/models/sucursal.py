import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.auditoria import Auditoria


class Sucursal(Base):
    __tablename__ = "sucursales"
    __table_args__ = {"schema": "auditchain"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200))
    region: Mapped[str] = mapped_column(String(100))
    direccion: Mapped[str | None] = mapped_column(Text)
    puntaje_promedio: Mapped[Decimal] = mapped_column(Numeric(5, 2), server_default="0")
    activo: Mapped[bool] = mapped_column(default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    auditorias: Mapped[list["Auditoria"]] = relationship(back_populates="sucursal")
