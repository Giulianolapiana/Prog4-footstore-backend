# app/modules/pedidos/repository.py
from sqlmodel import Session, select
from typing import List, Optional
from app.core.repository import BaseRepository
from app.modules.pedidos.models import (
    Pedido, EstadoPedido, FormaPago, HistorialEstadoPedido, DetallePedido
)

class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Pedido)

    def get_all_filtered(
        self, 
        skip: int = 0, 
        limit: int = 50, 
        usuario_id: Optional[int] = None, 
        estado_id: Optional[int] = None
    ) -> List[Pedido]:
        query = select(Pedido).where(Pedido.deleted_at == None)
        if usuario_id:
            query = query.where(Pedido.usuario_id == usuario_id)
        if estado_id:
            query = query.where(Pedido.estado_actual_id == estado_id)
        
        return self.session.exec(query.offset(skip).limit(limit)).all()

class EstadoPedidoRepository(BaseRepository[EstadoPedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, EstadoPedido)

    def get_by_codigo(self, codigo: str) -> EstadoPedido | None:
        return self.session.exec(
            select(EstadoPedido).where(EstadoPedido.codigo == codigo)
        ).first()

class FormaPagoRepository(BaseRepository[FormaPago]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, FormaPago)

class HistorialEstadoRepository(BaseRepository[HistorialEstadoPedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, HistorialEstadoPedido)

class DetallePedidoRepository(BaseRepository[DetallePedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DetallePedido)