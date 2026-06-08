from typing import List, Optional
from sqlmodel import Session, select, col
from app.core.repository import BaseRepository
from app.modules.categorias.models import Categoria
# Importamos el modelo de productos para chequear si hay activos
from app.modules.productos.models import ProductoCategoria, Producto

class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Categoria)

    def get_active(
        self,
        skip: int = 0,
        limit: int = 100,
        nombre: Optional[str] = None,
        parent_id: Optional[int] = None,
    ) -> List[Categoria]:
        query = select(Categoria).where(Categoria.deleted_at == None)
        
        if nombre:
            query = query.where(col(Categoria.nombre).icontains(nombre))
        
        # Agregamos el filtro requerido por el parcial
        if parent_id is not None:
            query = query.where(Categoria.parent_id == parent_id)
            
        query = query.order_by(Categoria.orden_display).offset(skip).limit(limit)
        return self.session.exec(query).all()

    def get_by_nombre(self, nombre: str) -> Categoria | None:
        return self.session.exec(
            select(Categoria).where(Categoria.nombre == nombre)
        ).first()

    def has_productos_activos(self, categoria_id: int) -> bool:
        """Verifica si la categoría tiene productos disponibles y no eliminados."""
        query = select(ProductoCategoria).join(Producto).where(
            ProductoCategoria.categoria_id == categoria_id,
            Producto.disponible == True,
            Producto.deleted_at == None
        )
        return self.session.exec(query).first() is not None
