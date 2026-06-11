from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.pagos.repository import PagoRepository
from app.modules.pedidos.repository import PedidoRepository, EstadoPedidoRepository, HistorialEstadoRepository

class PagoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.pagos = PagoRepository(session)
        self.pedidos = PedidoRepository(session)
        self.estados = EstadoPedidoRepository(session)
        self.historiales = HistorialEstadoRepository(session)