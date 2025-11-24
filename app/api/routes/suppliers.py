from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db_session, get_authenticated_user
from app.schemas.product_schemas import (
    ProveedorCreate,
    ProveedorRead,
    ProveedorUpdate,
)
from app.models.product_models import Proveedor

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.post("", response_model=ProveedorRead, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    payload: ProveedorCreate,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    supplier = Proveedor(**payload.dict())
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    return supplier


@router.get("", response_model=list[ProveedorRead])
async def list_suppliers(
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
    skip: int = 0,
    limit: int = Query(50, le=100),
    only_active: bool = True,
):
    query = select(Proveedor)
    if only_active:
        query = query.where(Proveedor.estado == True)  # noqa
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{supplier_id}", response_model=ProveedorRead)
async def get_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Proveedor).where(Proveedor.id_proveedor == supplier_id)
    )
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return supplier


@router.patch("/{supplier_id}", response_model=ProveedorRead)
async def update_supplier(
    supplier_id: int,
    payload: ProveedorUpdate,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Proveedor).where(Proveedor.id_proveedor == supplier_id)
    )
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(supplier, field, value)

    await db.commit()
    await db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Proveedor).where(Proveedor.id_proveedor == supplier_id)
    )
    supplier = result.scalar_one_or_none()
    if not supplier:
        return
    supplier.estado = False
    await db.commit()
