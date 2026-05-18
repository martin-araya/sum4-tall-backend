import uuid
from datetime import datetime
from typing import Annotated
from pydantic import Field, field_validator

from app.schemas.base import BaseSchema


class AuditoriaBase(BaseSchema):
    sucursal_id: uuid.UUID
    auditor_id: uuid.UUID
    fecha_programada: datetime
    observaciones: str | None = None


class AuditoriaCreate(AuditoriaBase):
    puntaje: Annotated[float | None, Field(default=None, ge=0, le=100)] = None

    @field_validator("puntaje")
    @classmethod
    def puntaje_rango(cls, v: float | None) -> float | None:
        if v is not None and not (0 <= v <= 100):
            raise ValueError("puntaje debe estar entre 0 y 100")
        return v


class AuditoriaUpdate(BaseSchema):
    estado: str | None = None
    puntaje: Annotated[float | None, Field(default=None, ge=0, le=100)] = None
    observaciones: str | None = None
    fecha_realizada: datetime | None = None


class AuditoriaOut(AuditoriaBase):
    id: uuid.UUID
    estado: str
    puntaje: float | None
    sucursal_nombre: str
    auditor_nombre: str
    fecha_realizada: datetime | None = None
    creado_en: datetime
