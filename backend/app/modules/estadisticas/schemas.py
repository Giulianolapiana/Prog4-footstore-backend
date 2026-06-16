from pydantic import BaseModel
from typing import List
from decimal import Decimal

class ResumenResponse(BaseModel):
    ventas_hoy: Decimal
    ticket_promedio: Decimal
    pedidos_activos: int
    ventas_mes_actual: Decimal

class VentasPeriodoItem(BaseModel):
    periodo: str
    total_ventas: Decimal
    cantidad_pedidos: int

class ProductoTopItem(BaseModel):
    nombre: str
    cantidad_vendida: int
    ingresos: Decimal

class PedidosEstadoItem(BaseModel):
    estado_codigo: str
    cantidad: int

class FormaPagoIngresoItem(BaseModel):
    forma_pago_codigo: str
    total: Decimal

class IngresosResponse(BaseModel):
    ingresos_por_forma_pago: List[FormaPagoIngresoItem]
