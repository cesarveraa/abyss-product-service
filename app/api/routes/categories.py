from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db_session, get_authenticated_user
from app.schemas.product_schemas import (
    CategoriaCreate,
    CategoriaRead,
)
from app.models.product_models import Categoria

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoriaCreate,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    category = Categoria(**payload.dict())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.get("", response_model=list[CategoriaRead])
async def list_categories(
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
    skip: int = 0,
    limit: int = Query(50, le=100),
):
    result = await db.execute(
        select(Categoria).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/{category_id}", response_model=CategoriaRead)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Categoria).where(Categoria.id_categoria == category_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category


@router.patch("/{category_id}", response_model=CategoriaRead)
async def update_category(
    category_id: int,
    payload: CategoriaCreate,   # mismo esquema, todo opcional si quieres
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Categoria).where(Categoria.id_categoria == category_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Categoria).where(Categoria.id_categoria == category_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        return

    await db.delete(category)
    await db.commit()
