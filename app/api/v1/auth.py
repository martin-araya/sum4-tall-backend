from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.usuario import UsuarioCreate, UsuarioOut
from app.services import auth_service, usuario_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
) -> UsuarioOut:
    return await usuario_service.create(db, schema=payload)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await auth_service.login(db, email=payload.email, password=payload.password)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await auth_service.refresh(db, refresh_token=payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    _current_user: Usuario = Depends(get_current_user),
) -> dict[str, str]:
    return {"message": "ok"}
