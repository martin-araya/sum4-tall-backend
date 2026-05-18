from fastapi import APIRouter

from app.api.v1 import auditores, auditorias, auth, sucursales, usuarios

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(usuarios.router)
router.include_router(sucursales.router)
router.include_router(auditores.router)
router.include_router(auditorias.router)
