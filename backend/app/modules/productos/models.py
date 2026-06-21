from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import JSON, Column, DECIMAL
from sqlmodel import SQLModel, Field, Relationship

# Importamos nuestro BaseEntity
from app.core.base_model import BaseEntity

if TYPE_CHECKING:
    from app.modules.categorias.models import Categoria
    from app.modules.ingredientes.models import Ingrediente

class UnidadMedida(BaseEntity, table=True):
    __tablename__ = "unidad_medida"
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=50, nullable=False, unique=True)
    simbolo: str = Field(max_length=10, nullable=False, unique=True)
    tipo: str = Field(max_length=20, nullable=False) # peso, volumen, contable

    productos: List["Producto"] = Relationship(back_populates="unidad_venta")

class ProductoCategoria(SQLModel, table=True):
    __tablename__ = "producto_categoria"
    producto_id: int = Field(foreign_key="producto.id", primary_key=True)
    categoria_id: int = Field(foreign_key="categoria.id", primary_key=True)
    es_principal: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingrediente"
    producto_id: int = Field(foreign_key="producto.id", primary_key=True)
    ingrediente_id: int = Field(foreign_key="ingrediente.id", primary_key=True)
    es_removible: bool = Field(default=True, nullable=False)
    es_opcional: bool = Field(default=False, nullable=False)
    cantidad: Decimal = Field(sa_column=Column(DECIMAL(10,3), nullable=False, server_default="1.000"), ge=0)
    unidad_medida_id: int = Field(foreign_key="unidad_medida.id", nullable=False, default=3)

    # Relaciones explícitas hacia Producto e Ingrediente y UnidadMedida
    producto: "Producto" = Relationship(back_populates="producto_ingredientes")
    ingrediente: "Ingrediente" = Relationship(back_populates="producto_ingredientes")
    unidad_medida: Optional["UnidadMedida"] = Relationship()

# Hereda de BaseEntity para tener created_at, updated_at y deleted_at automáticamente
class Producto(BaseEntity, table=True):
    __tablename__ = "producto"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=150, nullable=False)
    descripcion: Optional[str] = Field(default=None)
    stock_cantidad: int = Field(default=0, nullable=False, ge=0)
    precio_base: Decimal = Field(sa_column=Column(DECIMAL(10, 2), nullable=False), ge=0)
    imagenes_url: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    disponible: bool = Field(default=True, nullable=False)
    
    unidad_venta_id: Optional[int] = Field(default=None, foreign_key="unidad_medida.id")
    unidad_venta: Optional[UnidadMedida] = Relationship(back_populates="productos")

    # Eliminamos created_at, updated_at y deleted_at porque BaseEntity ya los trae

    categorias: List["Categoria"] = Relationship(
        back_populates="productos",
        link_model=ProductoCategoria
    )
    # Mantenemos ingredientes por compatibilidad si se requiere
    ingredientes: List["Ingrediente"] = Relationship(
        back_populates="productos",
        link_model=ProductoIngrediente
    )
    # Nueva relación a la tabla pivot para acceder a los campos extra
    producto_ingredientes: List["ProductoIngrediente"] = Relationship(
        back_populates="producto",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )