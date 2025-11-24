from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db_session, get_authenticated_user
from app.schemas.product_schemas import (
    UnidadMedidaCreate,
    UnidadMedidaRead,
)
from app.models.product_models import UnidadMedida

router = APIRouter(prefix="/units", tags=["units"])


@router.post("", response_model=UnidadMedidaRead, status_code=status.HTTP_201_CREATED)
async def create_unit(
    payload: UnidadMedidaCreate,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    unit = UnidadMedida(**payload.dict())
    db.add(unit)
    await db.commit()
    await db.refresh(unit)
    return unit


@router.get("", response_model=list[UnidadMedidaRead])
async def list_units(
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
    skip: int = 0,
    limit: int = Query(50, le=100),
):
    result = await db.execute(
        select(UnidadMedida).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/{unit_id}", response_model=UnidadMedidaRead)
async def get_unit(
    unit_id: int,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(UnidadMedida).where(UnidadMedida.id_unidad == unit_id)
    )
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    return unit


@router.patch("/{unit_id}", response_model=UnidadMedidaRead)
async def update_unit(
    unit_id: int,
    payload: UnidadMedidaCreate,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(UnidadMedida).where(UnidadMedida.id_unidad == unit_id)
    )
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")

    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(unit, field, value)

    await db.commit()
    await db.refresh(unit)
    return unit


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_unit(
    unit_id: int,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(UnidadMedida).where(UnidadMedida.id_unidad == unit_id)
    )
    unit = result.scalar_one_or_none()
    if not unit:
        return

    await db.delete(unit)
    await db.commit()
