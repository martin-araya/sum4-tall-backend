from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


class UsuarioRepository(BaseRepository[Usuario, UsuarioCreate, UsuarioUpdate]):
    model = Usuario

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_email(self, email: str) -> Usuario | None:
        result = await self.session.execute(
            select(Usuario).where(Usuario.email == email)
        )
        return result.scalar_one_or_none()

    async def authenticate(self, email: str, password: str) -> Usuario | None:
        user = await self.get_by_email(email)
        if user is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
