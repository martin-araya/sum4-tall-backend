import uuid
from datetime import datetime
from typing import Annotated
from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema


class UsuarioBase(BaseSchema):
    nombre: str
    email: EmailStr
    rol: str = "auditor"


class UsuarioCreate(UsuarioBase):
    password: Annotated[str, Field(min_length=8)]


class UsuarioUpdate(BaseSchema):
    nombre: str | None = None
    email: EmailStr | None = None
    activo: bool | None = None


class UsuarioOut(UsuarioBase):
    id: uuid.UUID
    activo: bool
    creado_en: datetime
