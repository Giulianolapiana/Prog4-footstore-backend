from datetime import date, datetime
from typing import List, Optional
from app.modules.estadisticas.repository import EstadisticasRepository
from app.modules.estadisticas.schemas import (
    ResumenResponse, VentasPeriodoItem, ProductoTopItem,
    PedidosEstadoItem, FormaPagoIngresoItem, IngresosResponse
)

class EstadisticasService:
    def __init__(self, repository: EstadisticasRepository):
        self._repository = repository

    def get_resumen_kpis(self) -> ResumenResponse:
        ventas_hoy, ticket_prom, pedidos_activos, ventas_mes = self._repository.get_kpis_resumen()

        return ResumenResponse(
            ventas_hoy=ventas_hoy,
            ticket_promedio=ticket_prom,
            pedidos_activos=pedidos_activos,
            ventas_mes_actual=ventas_mes
        )

    def get_ventas_periodo(self, desde: date, hasta: date, agrupacion: str = 'day') -> List[VentasPeriodoItem]:
        resultados = self._repository.get_ventas_periodo(desde, hasta, agrupacion)
        return [
            VentasPeriodoItem(
                periodo=str(r.periodo.date() if hasattr(r.periodo, 'date') else r.periodo) if r.periodo else "",
                total_ventas=r.total_ventas if r.total_ventas else 0.0,
                cantidad_pedidos=r.cantidad_pedidos
            ) for r in resultados
        ]

    def get_productos_top(self, limit: int = 5) -> List[ProductoTopItem]:
        resultados = self._repository.get_productos_top(limit)
        return [
            ProductoTopItem(
                nombre=r.nombre_snapshot,
                cantidad_vendida=r.cantidad_vendida,
                ingresos=r.ingresos if r.ingresos else 0.0
            ) for r in resultados
        ]

    def get_pedidos_por_estado(self) -> List[PedidosEstadoItem]:
        resultados = self._repository.get_pedidos_por_estado()
        return [
            PedidosEstadoItem(estado_codigo=r.codigo, cantidad=r.cantidad)
            for r in resultados
        ]

    def get_ingresos_por_forma_pago(self, desde: Optional[date] = None, hasta: Optional[date] = None) -> IngresosResponse:
        d_desde = desde or date(2000, 1, 1)
        d_hasta = hasta or date(2100, 1, 1)

        resultados = self._repository.get_ingresos_por_forma_pago(d_desde, d_hasta)
        items = [FormaPagoIngresoItem(forma_pago_codigo=r.codigo, total=r.total if r.total else 0.0) for r in resultados]
        return IngresosResponse(ingresos_por_forma_pago=items)
