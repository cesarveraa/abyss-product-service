from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr
from typing import Optional, List


# ---------- Proveedores ----------

class ProveedorBase(BaseModel):
    nombre: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    estado: bool = True


class ProveedorCreate(ProveedorBase):
    empresas_id_emp: int


class ProveedorUpdate(ProveedorBase):
    pass


class ProveedorRead(ProveedorBase):
    id_proveedor: int

    class Config:
        from_attributes = True


# ---------- Unidades ----------

class UnidadMedidaBase(BaseModel):
    codigo: str
    descripcion: Optional[str] = None
    es_fraccionable: bool = False


class UnidadMedidaCreate(UnidadMedidaBase):
    pass


class UnidadMedidaRead(UnidadMedidaBase):
    id_unidad: int

    class Config:
        from_attributes = True


# ---------- Categorías ----------

class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaRead(CategoriaBase):
    id_categoria: int

    class Config:
        from_attributes = True


# ---------- Atributos de producto ----------

class ProductoAtributoBase(BaseModel):
    nombre_atributo: str
    valor: Optional[str] = None


class ProductoAtributoCreate(ProductoAtributoBase):
    pass


class ProductoAtributoRead(ProductoAtributoBase):
    id_atributo: int

    class Config:
        from_attributes = True


# ---------- Productos ----------

class ProductoBase(BaseModel):
    codigo_sku: str
    codigo_barra: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    stock_minimo_global: int = 0
    estado: bool = True
    precio: Decimal
    proveedores_id_proveedor: int
    unidades_medida_id_unidad: int


class ProductoCreate(ProductoBase):
    categorias_ids: List[int] = []
    atributos: List[ProductoAtributoCreate] = []


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    stock_minimo_global: Optional[int] = None
    estado: Optional[bool] = None
    precio: Optional[Decimal] = None
    categorias_ids: Optional[List[int]] = None
    atributos: Optional[List[ProductoAtributoCreate]] = None


class ProductoRead(ProductoBase):
    id_producto: int
    fecha_creacion: datetime
    proveedor: ProveedorRead
    unidad_medida: UnidadMedidaRead
    categorias: List[CategoriaRead]
    atributos: List[ProductoAtributoRead]

    class Config:
        from_attributes = True
