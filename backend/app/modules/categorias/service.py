from typing import List, Optional
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.categorias.models import Categoria
from app.modules.categorias.schemas import CategoriaCreate, CategoriaUpdate
from app.modules.categorias.unit_of_work import CategoriaUnitOfWork

class CategoriaService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        nombre: Optional[str] = None,
        parent_id: Optional[int] = None,
    ) -> List[Categoria]:
        with CategoriaUnitOfWork(self._session) as uow:
            return uow.categorias.get_active(skip, limit, nombre, parent_id)

    def get_by_id(self, categoria_id: int) -> Categoria:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = uow.categorias.get_by_id(categoria_id)
            if not categoria or getattr(categoria, "deleted_at", None) is not None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Categoría con id={categoria_id} no encontrada."
                )
        return categoria

    def create(self, data: CategoriaCreate) -> Categoria:
        with CategoriaUnitOfWork(self._session) as uow:
            existente = uow.categorias.get_by_nombre(data.nombre)
            if existente:
                if getattr(existente, "deleted_at", None) is not None:
                    existente.deleted_at = None
                    existente.descripcion = data.descripcion
                    existente.orden_display = data.orden_display
                    uow.categorias.update(existente)
                    return existente
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe una categoría activa con el nombre '{data.nombre}'."
                )

            if data.parent_id is not None:
                parent = uow.categorias.get_by_id(data.parent_id)
                if not parent or getattr(parent, "deleted_at", None) is not None:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Categoría padre con id={data.parent_id} no encontrada."
                    )

            categoria = Categoria(**data.model_dump())
            uow.categorias.add(categoria)
        return categoria

    def update(self, categoria_id: int, data: CategoriaUpdate) -> Categoria:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = uow.categorias.get_by_id(categoria_id)
            if not categoria or getattr(categoria, "deleted_at", None) is not None:
                raise HTTPException(status_code=404, detail="Categoría no encontrada.")

            if data.nombre and data.nombre != categoria.nombre:
                existente = uow.categorias.get_by_nombre(data.nombre)
                if existente and getattr(existente, "deleted_at", None) is None:
                    raise HTTPException(status_code=409, detail="Nombre duplicado.")

            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(categoria, key, value)
            uow.categorias.update(categoria)
        return categoria

    def delete(self, categoria_id: int) -> None:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = uow.categorias.get_by_id(categoria_id)
            if not categoria or getattr(categoria, "deleted_at", None) is not None:
                raise HTTPException(status_code=404, detail="Categoría no encontrada.")
            
            # REQUISITO: Validar que no tenga productos activos antes de borrar
            if uow.categorias.has_productos_activos(categoria_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="No se puede eliminar la categoría porque tiene productos activos."
                )
            
            uow.categorias.delete(categoria)