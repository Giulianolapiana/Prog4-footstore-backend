from typing import List, Optional
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlmodel import Session
from app.modules.ingredientes.models import Ingrediente
from app.modules.ingredientes.schemas import IngredienteCreate, IngredienteUpdate
from app.modules.ingredientes.unit_of_work import IngredienteUnitOfWork


class IngredienteService:

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        nombre: Optional[str] = None,
        solo_alergenos: Optional[bool] = None,
    ) -> List[Ingrediente]:
        with IngredienteUnitOfWork(self._session) as uow:
            return uow.ingredientes.get_active(skip, limit, nombre, solo_alergenos)

    def get_by_id(self, ingrediente_id: int) -> Ingrediente:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
            if not ingrediente or ingrediente.deleted_at is not None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Ingrediente con id={ingrediente_id} no encontrado."
                )
        return ingrediente

    def create(self, data: IngredienteCreate) -> Ingrediente:
        with IngredienteUnitOfWork(self._session) as uow:
            existente = uow.ingredientes.get_by_nombre(data.nombre)
            if existente:
                if existente.deleted_at is not None:
                    # Reactivar
                    existente.deleted_at = None
                    existente.descripcion = data.descripcion
                    existente.es_alergeno = data.es_alergeno
                    existente.updated_at = datetime.now(timezone.utc)
                    uow.ingredientes.add(existente)
                    return existente
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe un ingrediente activo con el nombre '{data.nombre}'."
                )

            ingrediente = Ingrediente(**data.model_dump())
            uow.ingredientes.add(ingrediente)
        return ingrediente

    def update(self, ingrediente_id: int, data: IngredienteUpdate) -> Ingrediente:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
            if not ingrediente or ingrediente.deleted_at is not None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Ingrediente con id={ingrediente_id} no encontrado."
                )

            if data.nombre and data.nombre != ingrediente.nombre:
                existente = uow.ingredientes.get_by_nombre(data.nombre)
                if existente and existente.deleted_at is None:
                    raise HTTPException(
                        status_code=409,
                        detail=f"Ya existe un ingrediente con el nombre '{data.nombre}'."
                    )

            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(ingrediente, key, value)
            ingrediente.updated_at = datetime.now(timezone.utc)
            uow.ingredientes.add(ingrediente)
        return ingrediente

    def delete(self, ingrediente_id: int) -> None:
        """Delega el Soft-delete al repositorio base."""
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
            if not ingrediente or ingrediente.deleted_at is not None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Ingrediente con id={ingrediente_id} no encontrado."
                )
            # Llamamos al delete del repositorio genérico que ya hace la magia
            uow.ingredientes.delete(ingrediente)
