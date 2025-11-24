from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db_session, get_authenticated_user
from app.schemas.product_schemas import (
    ProductoAtributoCreate,
    ProductoAtributoRead,
)
from app.models.product_models import Producto, ProductoAtributo

router = APIRouter(prefix="/products", tags=["product-attributes"])


@router.get("/{product_id}/attributes", response_model=list[ProductoAtributoRead])
async def list_attributes(
    product_id: int,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Producto).where(Producto.id_producto == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product.atributos


@router.post(
    "/{product_id}/attributes",
    response_model=ProductoAtributoRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_attribute(
    product_id: int,
    payload: ProductoAtributoCreate,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Producto).where(Producto.id_producto == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    attr = ProductoAtributo(
        nombre_atributo=payload.nombre_atributo,
        valor=payload.valor,
        producto=product,
    )
    db.add(attr)
    await db.commit()
    await db.refresh(attr)
    return attr


@router.delete(
    "/{product_id}/attributes/{attr_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_attribute(
    product_id: int,
    attr_id: int,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(ProductoAtributo).where(
            ProductoAtributo.id_atributo == attr_id,
            ProductoAtributo.productos_id_prod == product_id,
        )
    )
    attr = result.scalar_one_or_none()
    if not attr:
        return

    await db.delete(attr)
    await db.commit()
