from fastapi import HTTPException, status
from sqlmodel import Session
from typing import Sequence
from app.modules.direcciones.models import DireccionEntrega
from app.modules.direcciones.schemas import DireccionCreate
from app.modules.direcciones.unit_of_work import DireccionUnitOfWork

class DireccionService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def listar_mis_direcciones(self, usuario_id: int) -> Sequence[DireccionEntrega]:
        with DireccionUnitOfWork(self._session) as uow:
            return uow.direcciones.get_by_usuario(usuario_id)

    def crear(self, usuario_id: int, data: DireccionCreate) -> DireccionEntrega:
        with DireccionUnitOfWork(self._session) as uow:
            # Si quiere que esta sea la principal, desmarcamos las demás
            if data.es_principal:
                uow.direcciones.desmarcar_principales(usuario_id)
            
            nueva_direccion = DireccionEntrega(
                usuario_id=usuario_id,
                **data.model_dump()
            )
            uow.direcciones.add(nueva_direccion)
            return nueva_direccion

    def marcar_principal(self, direccion_id: int, usuario_id: int) -> DireccionEntrega:
        with DireccionUnitOfWork(self._session) as uow:
            direccion = uow.direcciones.get_by_id(direccion_id)
            if not direccion or direccion.usuario_id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Dirección no encontrada"
                )
            
            uow.direcciones.desmarcar_principales(usuario_id)
            direccion.es_principal = True
            uow.direcciones.update(direccion)
            return direccion

    def eliminar(self, direccion_id: int, usuario_id: int) -> None:
        with DireccionUnitOfWork(self._session) as uow:
            direccion = uow.direcciones.get_by_id(direccion_id)
            if not direccion or direccion.usuario_id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Dirección no encontrada"
                )
            uow.direcciones.delete(direccion)