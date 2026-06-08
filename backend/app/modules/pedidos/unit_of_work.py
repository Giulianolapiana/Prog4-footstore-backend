# app/modules/pedidos/unit_of_work.py
from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.pedidos.repository import (
    PedidoRepository, EstadoPedidoRepository, FormaPagoRepository, 
    HistorialEstadoRepository, DetallePedidoRepository
)
# Necesitamos acceder a productos para el Snapshot y a direcciones para validar
from app.modules.productos.repository import ProductoRepository
from app.modules.direcciones.repository import DireccionRepository

class PedidoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.pedidos = PedidoRepository(session)
        self.estados = EstadoPedidoRepository(session)
        self.formas_pago = FormaPagoRepository(session)
        self.historiales = HistorialEstadoRepository(session)
        self.detalles = DetallePedidoRepository(session)
        self.productos = ProductoRepository(session)
        self.direcciones = DireccionRepository(session)