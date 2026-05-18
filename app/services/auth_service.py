import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import TokenResponse


async def login(db: AsyncSession, email: str, password: str) -> TokenResponse:
    repo = UsuarioRepository(db)
    user = await repo.authenticate(email, password)

    if user is None:
        raise AuthenticationError("Credenciales inválidas")

    if not user.activo:
        raise AuthenticationError("Usuario inactivo")

    sub = str(user.id)
    return TokenResponse(
        access_token=create_access_token({"sub": sub, "rol": user.rol}),
        refresh_token=create_refresh_token({"sub": sub}),
        user_name=user.nombre,
        user_role=user.rol,
    )


async def refresh(db: AsyncSession, refresh_token: str) -> TokenResponse:
    payload = verify_token(refresh_token, expected_type="refresh")

    sub = payload.get("sub")
    if not sub:
        raise AuthenticationError("Refresh token sin subject")

    try:
        user_id = uuid.UUID(sub)
    except ValueError:
        raise AuthenticationError("Refresh token inválido")

    repo = UsuarioRepository(db)
    user = await repo.get(user_id)

    if user is None or not user.activo:
        raise AuthenticationError("Usuario no encontrado o inactivo")

    sub_str = str(user.id)
    return TokenResponse(
        access_token=create_access_token({"sub": sub_str, "rol": user.rol}),
        refresh_token=create_refresh_token({"sub": sub_str}),
        user_name=user.nombre,
        user_role=user.rol,
    )
