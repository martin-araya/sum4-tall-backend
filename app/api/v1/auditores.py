import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user, get_db
from app.models.usuario import Usuario
from app.schemas.auditor import AuditorCreate, AuditorOut, AuditorUpdate
from app.schemas.common import PaginatedResponse
from app.services import auditor_service

router = APIRouter(prefix="/auditores", tags=["Auditores"])


@router.get("", response_model=PaginatedResponse[AuditorOut])
async def list_auditores(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    activos_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> PaginatedResponse[AuditorOut]:
    return await auditor_service.get_all(
        db, page=page, size=size, activos_only=activos_only
    )


@router.get("/{id}", response_model=AuditorOut)
async def get_auditor(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> AuditorOut:
    return await auditor_service.get_by_id(db, id)


@router.post("", response_model=AuditorOut, status_code=status.HTTP_201_CREATED)
async def create_auditor(
    payload: AuditorCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_admin),
) -> AuditorOut:
    return await auditor_service.create(db, payload)


@router.put("/{id}", response_model=AuditorOut)
async def update_auditor(
    id: uuid.UUID,
    payload: AuditorUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_admin),
) -> AuditorOut:
    return await auditor_service.update(db, id, payload)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_auditor(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_admin),
) -> None:
    await auditor_service.delete(db, id)
