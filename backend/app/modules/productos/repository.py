from typing import List, Optional
from decimal import Decimal
from sqlmodel import Session, select, col
from app.core.repository import BaseRepository
from app.modules.productos.models import Producto, ProductoCategoria, ProductoIngrediente


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Producto)

    def search(
        self,
        skip: int = 0,
        limit: int = 100,
        nombre: Optional[str] = None,
        disponible: Optional[bool] = None,
        precio_min: Optional[Decimal] = None,
        precio_max: Optional[Decimal] = None,
    ) -> tuple[List[Producto], int]:
        from sqlmodel import func
        query = select(Producto).where(Producto.deleted_at.is_(None))
        if nombre:
            query = query.where(col(Producto.nombre).icontains(nombre))
        if disponible is not None:
            query = query.where(Producto.disponible == disponible)
        if precio_min is not None:
            query = query.where(Producto.precio_base >= precio_min)
        if precio_max is not None:
            query = query.where(Producto.precio_base <= precio_max)
        
        total = self.session.exec(select(func.count()).select_from(query.subquery())).one()
        items = self.session.exec(
            query.order_by(Producto.nombre).offset(skip).limit(limit)
        ).all()
        return items, total

    def get_categorias_links(self, producto_id: int) -> List[ProductoCategoria]:
        return self.session.exec(
            select(ProductoCategoria).where(
                ProductoCategoria.producto_id == producto_id
            )
        ).all()

    def get_ingredientes_links(self, producto_id: int) -> List[ProductoIngrediente]:
        return self.session.exec(
            select(ProductoIngrediente).where(
                ProductoIngrediente.producto_id == producto_id
            )
        ).all()

    def get_by_nombre(self, nombre: str) -> Optional[Producto]:
        return self.session.exec(select(Producto).where(Producto.nombre == nombre)).first()

    def add_categoria_link(self, link: ProductoCategoria) -> None:
        self.session.add(link)

    def add_ingrediente_link(self, link: ProductoIngrediente) -> None:
        self.session.add(link)

    def delete_categoria_link(self, link: ProductoCategoria) -> None:
        self.session.delete(link)

    def delete_ingrediente_link(self, link: ProductoIngrediente) -> None:
        self.session.delete(link)
