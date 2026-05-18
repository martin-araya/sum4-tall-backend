from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioOut, UsuarioUpdate
from app.services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/me", response_model=UsuarioOut)
async def get_me(
    current_user: Usuario = Depends(get_current_user),
) -> UsuarioOut:
    return UsuarioOut.model_validate(current_user)


@router.put("/me", response_model=UsuarioOut)
async def update_me(
    payload: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> UsuarioOut:
    # El usuario no puede auto-desactivarse ni cambiar su rol vía /me.
    safe_payload = UsuarioUpdate(
        nombre=payload.nombre,
        email=payload.email,
    )
    return await usuario_service.update(db, current_user.id, safe_payload)
