from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    ForeignKey,
    Table,
    DateTime,
    Numeric,
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# Tabla pivot categorias_productos
categorias_productos = Table(
    "categorias_productos",
    Base.metadata,
    Column("categorias_categoria", Integer, ForeignKey("categorias.id_categoria"), primary_key=True),
    Column("productos_producto", Integer, ForeignKey("productos.id_producto"), primary_key=True),
)


class Proveedor(Base):
    __tablename__ = "proveedores"

    id_proveedor = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(30), nullable=False)
    contacto = Column(String(30))
    telefono = Column(String(15))
    email = Column(String(30))
    direccion = Column(String(200))
    estado = Column(Boolean, default=True)
    empresas_id_emp = Column(Integer)

    productos = relationship("Producto", back_populates="proveedor")


class UnidadMedida(Base):
    __tablename__ = "unidades_medida"

    id_unidad = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(100), nullable=False)
    descripcion = Column(String(300))
    es_fraccionable = Column(Boolean, default=False)

    productos = relationship("Producto", back_populates="unidad_medida")


class Categoria(Base):
    __tablename__ = "categorias"

    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(30), nullable=False)
    descripcion = Column(String(300))

    productos = relationship(
        "Producto",
        secondary=categorias_productos,
        back_populates="categorias",
    )


class Producto(Base):
    __tablename__ = "productos"

    id_producto = Column(Integer, primary_key=True, index=True)
    codigo_sku = Column(String(100), nullable=False, unique=True)
    codigo_barra = Column(String(100), unique=True)
    nombre = Column(String(30), nullable=False)
    descripcion = Column(String(300))
    stock_minimo_global = Column(Integer, default=0)
    estado = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    precio = Column(Numeric(12, 2), nullable=False)

    proveedores_id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"))
    unidades_medida_id_unidad = Column(Integer, ForeignKey("unidades_medida.id_unidad"))

    proveedor = relationship("Proveedor", back_populates="productos")
    unidad_medida = relationship("UnidadMedida", back_populates="productos")
    categorias = relationship(
        "Categoria",
        secondary=categorias_productos,
        back_populates="productos",
    )
    atributos = relationship(
        "ProductoAtributo",
        back_populates="producto",
        cascade="all, delete-orphan",
    )


class ProductoAtributo(Base):
    __tablename__ = "productos_atributos"

    id_atributo = Column(Integer, primary_key=True, index=True)
    nombre_atributo = Column(String(30), nullable=False)
    valor = Column(String(300))
    productos_id_prod = Column(Integer, ForeignKey("productos.id_producto"))

    producto = relationship("Producto", back_populates="atributos")
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    ForeignKey,
    Table,
    DateTime,
    Numeric,
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# Tabla pivot categorias_productos
categorias_productos = Table(
    "categorias_productos",
    Base.metadata,
    Column("categorias_categoria", Integer, ForeignKey("categorias.id_categoria"), primary_key=True),
    Column("productos_producto", Integer, ForeignKey("productos.id_producto"), primary_key=True),
)


class Proveedor(Base):
    __tablename__ = "proveedores"

    id_proveedor = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(30), nullable=False)
    contacto = Column(String(30))
    telefono = Column(String(15))
    email = Column(String(30))
    direccion = Column(String(200))
    estado = Column(Boolean, default=True)
    empresas_id_emp = Column(Integer)

    productos = relationship("Producto", back_populates="proveedor")


class UnidadMedida(Base):
    __tablename__ = "unidades_medida"

    id_unidad = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(100), nullable=False)
    descripcion = Column(String(300))
    es_fraccionable = Column(Boolean, default=False)

    productos = relationship("Producto", back_populates="unidad_medida")


class Categoria(Base):
    __tablename__ = "categorias"

    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(30), nullable=False)
    descripcion = Column(String(300))

    productos = relationship(
        "Producto",
        secondary=categorias_productos,
        back_populates="categorias",
    )


class Producto(Base):
    __tablename__ = "productos"

    id_producto = Column(Integer, primary_key=True, index=True)
    codigo_sku = Column(String(100), nullable=False, unique=True)
    codigo_barra = Column(String(100), unique=True)
    nombre = Column(String(30), nullable=False)
    descripcion = Column(String(300))
    stock_minimo_global = Column(Integer, default=0)
    estado = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    precio = Column(Numeric(12, 2), nullable=False)

    proveedores_id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"))
    unidades_medida_id_unidad = Column(Integer, ForeignKey("unidades_medida.id_unidad"))

    proveedor = relationship("Proveedor", back_populates="productos")
    unidad_medida = relationship("UnidadMedida", back_populates="productos")
    categorias = relationship(
        "Categoria",
        secondary=categorias_productos,
        back_populates="productos",
    )
    atributos = relationship(
        "ProductoAtributo",
        back_populates="producto",
        cascade="all, delete-orphan",
    )


class ProductoAtributo(Base):
    __tablename__ = "productos_atributos"

    id_atributo = Column(Integer, primary_key=True, index=True)
    nombre_atributo = Column(String(30), nullable=False)
    valor = Column(String(300))
    productos_id_prod = Column(Integer, ForeignKey("productos.id_producto"))

    producto = relationship("Producto", back_populates="atributos")
