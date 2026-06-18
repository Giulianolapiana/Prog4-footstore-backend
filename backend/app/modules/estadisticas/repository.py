from sqlmodel import Session, select, func, cast, String
from sqlalchemy import Date
from datetime import date
from typing import List, Tuple, Optional
from decimal import Decimal
from app.modules.pedidos.models import Pedido, DetallePedido, EstadoPedido, FormaPago
from app.modules.pagos.models import Pago

class EstadisticasRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_ventas_periodo(self, desde: date, hasta: date, agrupacion: str) -> List[Tuple]:
        stmt = (
            select(
                cast(func.date_trunc(agrupacion, Pedido.created_at), String).label("periodo"),
                func.sum(Pedido.total).label("total_ventas"),
                func.count(Pedido.id).label("cantidad_pedidos")
            )
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .outerjoin(Pago, Pago.pedido_id == Pedido.id)
            .join(FormaPago, FormaPago.id == Pedido.forma_pago_id)
            .where(EstadoPedido.codigo != "CANCELADO")
            .where(
                (Pago.mp_status == "approved") | 
                (Pago.estado == "aprobado") | 
                (FormaPago.codigo.in_(["EFECTIVO", "CREDIT", "DEBIT"]))
            )
            .where(cast(Pedido.created_at, Date).between(desde, hasta))
            .group_by("periodo")
            .order_by("periodo")
        )
        return self.session.exec(stmt).all()

    def get_productos_top(self, limit: int = 5) -> List[Tuple]:
        stmt = (
            select(
                DetallePedido.nombre_snapshot,
                func.sum(DetallePedido.subtotal_snap).label("ingresos"),
                func.sum(DetallePedido.cantidad).label("cantidad_vendida")
            )
            .join(Pedido)
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .outerjoin(Pago, Pago.pedido_id == Pedido.id)
            .join(FormaPago, FormaPago.id == Pedido.forma_pago_id)
            .where(EstadoPedido.codigo != "CANCELADO")
            .where(
                (Pago.mp_status == "approved") | 
                (Pago.estado == "aprobado") | 
                (FormaPago.codigo.in_(["EFECTIVO", "CREDIT", "DEBIT"]))
            )
            .group_by(DetallePedido.nombre_snapshot)
            .order_by(func.sum(DetallePedido.subtotal_snap).desc())
            .limit(limit)
        )
        return self.session.exec(stmt).all()

    def get_pedidos_por_estado(self) -> List[Tuple]:
        stmt = (
            select(EstadoPedido.codigo, func.count(Pedido.id).label("cantidad"))
            .join(Pedido)
            .group_by(EstadoPedido.codigo)
        )
        return self.session.exec(stmt).all()

    def get_ingresos_por_forma_pago(self, desde: date, hasta: date) -> List[Tuple]:
        stmt = (
            select(
                FormaPago.codigo,
                func.sum(Pedido.total).label("total"),
                func.count(Pedido.id).label("cantidad")
            )
            .join(Pedido, FormaPago.id == Pedido.forma_pago_id)
            .join(EstadoPedido, EstadoPedido.id == Pedido.estado_actual_id)
            .outerjoin(Pago, Pago.pedido_id == Pedido.id)
            .where(EstadoPedido.codigo != "CANCELADO")
            .where(cast(Pedido.created_at, Date).between(desde, hasta))
            .where(
                (Pago.mp_status == "approved") | 
                (Pago.estado == "aprobado") | 
                (FormaPago.codigo.in_(["EFECTIVO", "CREDIT", "DEBIT"]))
            )
            .group_by(FormaPago.codigo)
        )
        return self.session.exec(stmt).all()

    def get_kpis_resumen(self) -> Tuple[Decimal, Decimal, int, Decimal]:
        hoy = date.today()
        inicio_mes = hoy.replace(day=1)

        ventas_hoy = self.session.exec(
            select(func.sum(Pedido.total))
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .outerjoin(Pago, Pago.pedido_id == Pedido.id)
            .join(FormaPago, FormaPago.id == Pedido.forma_pago_id)
            .where(EstadoPedido.codigo != "CANCELADO")
            .where(
                (Pago.mp_status == "approved") | 
                (Pago.estado == "aprobado") | 
                (FormaPago.codigo.in_(["EFECTIVO", "CREDIT", "DEBIT"]))
            )
            .where(cast(Pedido.created_at, Date) == hoy)
        ).first() or Decimal('0.00')

        ticket_prom = self.session.exec(
            select(func.avg(Pedido.total))
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .outerjoin(Pago, Pago.pedido_id == Pedido.id)
            .join(FormaPago, FormaPago.id == Pedido.forma_pago_id)
            .where(EstadoPedido.codigo != "CANCELADO")
            .where(
                (Pago.mp_status == "approved") | 
                (Pago.estado == "aprobado") | 
                (FormaPago.codigo.in_(["EFECTIVO", "CREDIT", "DEBIT"]))
            )
        ).first() or Decimal('0.00')

        pedidos_activos = self.session.exec(
            select(func.count(Pedido.id))
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .where(EstadoPedido.codigo.in_(["PENDIENTE", "CONFIRMADO", "EN_PREP"]))
        ).first() or 0

        ventas_mes = self.session.exec(
            select(func.sum(Pedido.total))
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .outerjoin(Pago, Pago.pedido_id == Pedido.id)
            .join(FormaPago, FormaPago.id == Pedido.forma_pago_id)
            .where(EstadoPedido.codigo != "CANCELADO")
            .where(
                (Pago.mp_status == "approved") | 
                (Pago.estado == "aprobado") | 
                (FormaPago.codigo.in_(["EFECTIVO", "CREDIT", "DEBIT"]))
            )
            .where(cast(Pedido.created_at, Date) >= inicio_mes)
        ).first() or Decimal('0.00')

        return (ventas_hoy, ticket_prom, pedidos_activos, ventas_mes)