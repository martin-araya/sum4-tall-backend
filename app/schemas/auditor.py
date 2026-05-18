import uuid
from datetime import datetime
from pydantic import EmailStr

from app.schemas.base import BaseSchema


class AuditorBase(BaseSchema):
    nombre: str
    email: EmailStr
    region: str | None = None


class AuditorCreate(AuditorBase):
    usuario_id: uuid.UUID


class AuditorUpdate(BaseSchema):
    nombre: str | None = None
    email: EmailStr | None = None
    region: str | None = None
    activo: bool | None = None


class AuditorOut(AuditorBase):
    id: uuid.UUID
    usuario_id: uuid.UUID
    activo: bool
    creado_en: datetime
