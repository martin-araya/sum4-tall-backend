import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.usuario import Usuario
from app.schemas.auditoria import AuditoriaCreate, AuditoriaOut, AuditoriaUpdate
from app.schemas.common import PaginatedResponse
from app.services import auditoria_service

router = APIRouter(prefix="/auditorias", tags=["Auditorías"])


@router.get("", response_model=PaginatedResponse[AuditoriaOut])
async def list_auditorias(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    estado: str | None = Query(None),
    sucursal_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> PaginatedResponse[AuditoriaOut]:
    return await auditoria_service.get_all(
        db, page=page, size=size, estado=estado, sucursal_id=sucursal_id
    )


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> dict[str, Any]:
    return await auditoria_service.get_stats(db)


@router.get("/{id}", response_model=AuditoriaOut)
async def get_auditoria(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> AuditoriaOut:
    return await auditoria_service.get_by_id(db, id)


@router.post("", response_model=AuditoriaOut, status_code=status.HTTP_201_CREATED)
async def create_auditoria(
    payload: AuditoriaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> AuditoriaOut:
    return await auditoria_service.create(db, payload, current_user)


@router.put("/{id}", response_model=AuditoriaOut)
async def update_auditoria(
    id: uuid.UUID,
    payload: AuditoriaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> AuditoriaOut:
    return await auditoria_service.update(db, id, payload, current_user)
