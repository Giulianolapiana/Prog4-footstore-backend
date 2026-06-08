from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.core.base_model import BaseEntity
from app.modules.productos.models import ProductoIngrediente

if TYPE_CHECKING:
    from app.modules.productos.models import Producto

class Ingrediente(BaseEntity, table=True):
    __tablename__ = "ingrediente"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, nullable=False, unique=True)
    # Faltaba este campo que usás en tus schemas:
    descripcion: Optional[str] = Field(default=None, max_length=500) 
    es_alergeno: bool = Field(default=False, nullable=False)

    productos: List["Producto"] = Relationship(
        back_populates="ingredientes",
        link_model=ProductoIngrediente 
    )
