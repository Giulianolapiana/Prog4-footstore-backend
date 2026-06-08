from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.core.base_model import BaseEntity
from app.modules.productos.models import ProductoCategoria

if TYPE_CHECKING:
    from app.modules.productos.models import Producto

class Categoria(BaseEntity, table=True):
    __tablename__ = "categoria"

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    nombre: str = Field(max_length=100, unique=True, nullable=False)
    descripcion: Optional[str] = Field(default=None)
    orden_display: int = Field(default=0)

    # Relación N:M directa con Producto
    productos: List["Producto"] = Relationship(
        back_populates="categorias",
        link_model=ProductoCategoria
    )

    # Relación jerárquica 1:N self-referencial
    parent: Optional["Categoria"] = Relationship(
        back_populates="subcategorias",
        sa_relationship_kwargs=dict(remote_side="Categoria.id")
    )
    subcategorias: List["Categoria"] = Relationship(
        back_populates="parent"
    )