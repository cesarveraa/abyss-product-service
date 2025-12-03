from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_db_session, get_authenticated_user
from app.schemas.product_schemas import (
    ProductoCreate,
    ProductoRead,
    ProductoUpdate,
)
from app.models.product_models import Producto, Categoria, ProductoAtributo

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductoCreate,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    existing = await db.execute(
        select(Producto).where(Producto.codigo_sku == payload.codigo_sku)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="codigo_sku ya existe")

    product = Producto(
    codigo_sku=payload.codigo_sku,
    codigo_barra=payload.codigo_barra,
    nombre=payload.nombre,
    descripcion=payload.descripcion,
    stock_minimo_global=payload.stock_minimo_global,
    estado=payload.estado,
    precio=payload.precio,
    proveedores_id_proveedor=payload.proveedores_id_proveedor,
    unidades_medida_id_unidad=payload.unidades_medida_id_unidad,
    empresas_id_empresa=payload.empresas_id_empresa,  
)



    # categorías
    if payload.categorias_ids:
        result = await db.execute(
            select(Categoria).where(
                Categoria.id_categoria.in_(payload.categorias_ids)
            )
        )
        product.categorias = result.scalars().all()

    # atributos
    for attr in payload.atributos:
        product.atributos.append(
            ProductoAtributo(
                nombre_atributo=attr.nombre_atributo,
                valor=attr.valor,
            )
        )

    db.add(product)
    await db.commit()
    await db.refresh(product)

    # 🔥 recargar el producto con todas sus relaciones para evitar lazy-load async
    result = await db.execute(
        select(Producto)
        .options(
            selectinload(Producto.proveedor),
            selectinload(Producto.unidad_medida),
            selectinload(Producto.categorias),
            selectinload(Producto.atributos),
        )
        .where(Producto.id_producto == product.id_producto)
    )
    product_full = result.scalar_one()
    return product_full


@router.get("", response_model=list[ProductoRead])
async def list_products(
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
    skip: int = 0,
    limit: int = Query(50, le=100),
    search: str | None = None,
    categoria_id: int | None = None,
    proveedor_id: int | None = None,
    only_active: bool = True,
):
    # base query con relaciones
    query = (
        select(Producto)
        .options(
            selectinload(Producto.proveedor),
            selectinload(Producto.unidad_medida),
            selectinload(Producto.categorias),
            selectinload(Producto.atributos),
        )
    )

    if only_active:
        query = query.where(Producto.estado == True)  # noqa

    if search:
        like = f"%{search}%"
        query = query.where(
            (Producto.nombre.ilike(like))
            | (Producto.descripcion.ilike(like))
            | (Producto.codigo_sku.ilike(like))
        )

    if proveedor_id:
        query = query.where(Producto.proveedores_id_proveedor == proveedor_id)

    if categoria_id:
        query = query.join(Producto.categorias).where(
            Categoria.id_categoria == categoria_id
        )

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.get("/{product_id}", response_model=ProductoRead)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Producto)
        .options(
            selectinload(Producto.proveedor),
            selectinload(Producto.unidad_medida),
            selectinload(Producto.categorias),
            selectinload(Producto.atributos),
        )
        .where(Producto.id_producto == product_id)
    )

    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.patch("/{product_id}", response_model=ProductoRead)
async def update_product(
    product_id: int,
    payload: ProductoUpdate,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Producto).where(Producto.id_producto == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    data = payload.dict(exclude_unset=True)

    for field in ["nombre", "descripcion", "stock_minimo_global", "estado", "precio"]:
        if field in data:
            setattr(product, field, data[field])

    # actualización de categorías
    if "categorias_ids" in data and data["categorias_ids"] is not None:
        result = await db.execute(
            select(Categoria).where(
                Categoria.id_categoria.in_(data["categorias_ids"])
            )
        )
        product.categorias = result.scalars().all()

    # reemplazo completo de atributos
    if "atributos" in data and data["atributos"] is not None:
        # eliminar todos y volver a crear
        for attr in list(product.atributos):
            await db.delete(attr)
        product.atributos = []
        for attr in data["atributos"]:
            product.atributos.append(
                ProductoAtributo(
                    nombre_atributo=attr.nombre_atributo,
                    valor=attr.valor,
                )
            )

    await db.commit()
    await db.refresh(product)

    # recargar con relaciones
    result = await db.execute(
        select(Producto)
        .options(
            selectinload(Producto.proveedor),
            selectinload(Producto.unidad_medida),
            selectinload(Producto.categorias),
            selectinload(Producto.atributos),
        )
        .where(Producto.id_producto == product.id_producto)
    )
    product_full = result.scalar_one()
    return product_full


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db_session),
    _user=Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Producto).where(Producto.id_producto == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        return

    # soft delete
    product.estado = False
    await db.commit()
