from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlmodel import Session
from app.modules.productos.models import Producto, ProductoCategoria, ProductoIngrediente
from app.modules.productos.schemas import ProductoCreate, ProductoUpdate
from app.modules.productos.unit_of_work import ProductoUnitOfWork

class ProductoService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all(self, skip=0, limit=100, nombre=None, disponible=None, precio_min=None, precio_max=None) -> dict:
        with ProductoUnitOfWork(self._session) as uow:
            items, total = uow.productos.search(skip, limit, nombre, disponible, precio_min, precio_max)
            return {
                "items": items,
                "total": total,
                "page": (skip // limit) + 1 if limit > 0 else 1,
                "size": limit
            }

    def get_by_id(self, producto_id: int) -> Producto:
        with ProductoUnitOfWork(self._session) as uow:
            producto = uow.productos.get_by_id(producto_id)
            if not producto:
                raise HTTPException(status_code=404, detail="Producto no encontrado.")
        return producto

    def create(self, data: ProductoCreate) -> Producto:
        with ProductoUnitOfWork(self._session) as uow:
            existente = uow.productos.get_by_nombre(data.nombre)

            if existente:
                if existente.deleted_at is not None:
                    existente.deleted_at = None
                    update_data = data.model_dump(exclude={"categoria_ids", "ingredientes"})
                    for key, value in update_data.items():
                        setattr(existente, key, value)
                    
                    for link in uow.productos.get_categorias_links(existente.id):
                        uow.productos.delete_categoria_link(link)
                    for link in uow.productos.get_ingredientes_links(existente.id):
                        uow.productos.delete_ingrediente_link(link)

                    self._attach_categorias(uow, existente, data.categoria_ids)
                    self._attach_ingredientes(uow, existente, data.ingredientes)
                    uow.productos.update(existente)
                    return existente
                else:
                    raise HTTPException(status_code=409, detail="Ya existe un producto activo con ese nombre.")

            producto = Producto(**data.model_dump(exclude={"categoria_ids", "ingredientes"}))
            # uow.productos.add() inside BaseRepository already does flush() and refresh()
            producto = uow.productos.add(producto)
            self._attach_categorias(uow, producto, data.categoria_ids)
            self._attach_ingredientes(uow, producto, data.ingredientes)
            # update here simply to ensure any relationships added are refreshed/flushed properly if needed
            # though UOW commit will handle the insert.
            uow.productos.update(producto)
        return producto

    def update(self, producto_id: int, data: ProductoUpdate) -> Producto:
        with ProductoUnitOfWork(self._session) as uow:
            producto = uow.productos.get_by_id(producto_id)
            if not producto:
                raise HTTPException(status_code=404, detail="Producto no encontrado.")

            update_data = data.model_dump(exclude_unset=True, exclude={"categoria_ids", "ingredientes"})
            for key, value in update_data.items():
                setattr(producto, key, value)

            if data.categoria_ids is not None:
                for link in uow.productos.get_categorias_links(producto_id):
                    uow.productos.delete_categoria_link(link)
                self._attach_categorias(uow, producto, data.categoria_ids)

            if data.ingredientes is not None:
                for link in uow.productos.get_ingredientes_links(producto_id):
                    uow.productos.delete_ingrediente_link(link)
                self._attach_ingredientes(uow, producto, data.ingredientes)

            uow.productos.update(producto)
        return producto

    def patch_disponibilidad(self, producto_id: int, disponible: bool) -> Producto:
        with ProductoUnitOfWork(self._session) as uow:
            producto = uow.productos.get_by_id(producto_id)
            if not producto:
                raise HTTPException(status_code=404, detail="Producto no encontrado.")
            producto.disponible = disponible
            uow.productos.update(producto)
        return producto

    def delete(self, producto_id: int) -> None:
        with ProductoUnitOfWork(self._session) as uow:
            producto = uow.productos.get_by_id(producto_id)
            if not producto:
                raise HTTPException(status_code=404, detail="Producto no encontrado.")
            uow.productos.delete(producto)

    def _attach_categorias(self, uow, producto, categoria_ids) -> None:
        for i, cat_id in enumerate(categoria_ids):
            link = ProductoCategoria(producto_id=producto.id, categoria_id=cat_id, es_principal=(i == 0))
            uow.productos.add_categoria_link(link)

    def _attach_ingredientes(self, uow, producto, ingredientes_data) -> None:
        for ing_link in ingredientes_data:
            link = ProductoIngrediente(
                producto_id=producto.id,
                ingrediente_id=ing_link.ingrediente_id,
                es_removible=ing_link.es_removible,
                es_opcional=ing_link.es_opcional,
                cantidad=ing_link.cantidad,
                unidad_medida_id=ing_link.unidad_medida_id
            )
            uow.productos.add_ingrediente_link(link)
