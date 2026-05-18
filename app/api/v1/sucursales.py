import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user, get_db
from app.models.usuario import Usuario
from app.schemas.common import PaginatedResponse
from app.schemas.sucursal import SucursalCreate, SucursalOut, SucursalUpdate
from app.services import sucursal_service

router = APIRouter(prefix="/sucursales", tags=["Sucursales"])


@router.get("", response_model=PaginatedResponse[SucursalOut])
async def list_sucursales(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    region: str | None = Query(None),
    activas_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> PaginatedResponse[SucursalOut]:
    return await sucursal_service.get_all(
        db, page=page, size=size, region=region, activas_only=activas_only
    )


@router.get("/{id}", response_model=SucursalOut)
async def get_sucursal(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> SucursalOut:
    return await sucursal_service.get_by_id(db, id)


@router.post("", response_model=SucursalOut, status_code=status.HTTP_201_CREATED)
async def create_sucursal(
    payload: SucursalCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_admin),
) -> SucursalOut:
    return await sucursal_service.create(db, payload)


@router.put("/{id}", response_model=SucursalOut)
async def update_sucursal(
    id: uuid.UUID,
    payload: SucursalUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_admin),
) -> SucursalOut:
    return await sucursal_service.update(db, id, payload)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sucursal(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_admin),
) -> None:
    # delete vía soft-flag o hard-delete depende de la decisión final;
    # aquí usamos update para marcar inactiva, preservando integridad referencial.
    await sucursal_service.update(db, id, SucursalUpdate(activo=False))
