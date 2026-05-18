import uuid
from datetime import datetime
from app.schemas.base import BaseSchema


class SucursalBase(BaseSchema):
    nombre: str
    region: str
    direccion: str | None = None


class SucursalCreate(SucursalBase):
    pass


class SucursalUpdate(BaseSchema):
    nombre: str | None = None
    region: str | None = None
    direccion: str | None = None
    activo: bool | None = None


class SucursalOut(SucursalBase):
    id: uuid.UUID
    puntaje_promedio: float | None = None
    activo: bool
    creado_en: datetime
