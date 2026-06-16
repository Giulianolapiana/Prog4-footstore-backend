# app/modules/pedidos/schemas.py
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.modules.direcciones.schemas import DireccionResponse

# SCHEMAS PARA CREACION Desde el carrito
class DetallePedidoCreate(BaseModel):
    producto_id: int
    cantidad: int

class PedidoCreate(BaseModel):
    direccion_entrega_id: int
    forma_pago_id: int
    detalles: List[DetallePedidoCreate]

class AvanzarEstadoRequest(BaseModel):
    estado_codigo: str

# SCHEMAS DE RESPUESTA 
class EstadoPedidoResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    model_config = ConfigDict(from_attributes=True)

class FormaPagoResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    model_config = ConfigDict(from_attributes=True)

class HistorialEstadoResponse(BaseModel):
    id: int
    estado_desde: Optional[str] = None
    estado_hacia: str
    usuario_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DetallePedidoResponse(BaseModel):
    id: int
    producto_id: int
    producto_nombre: str
    producto_precio: float
    cantidad: int
    subtotal: float
    model_config = ConfigDict(from_attributes=True)

class PedidoResponse(BaseModel):
    id: int
    usuario_id: int
    total: float
    created_at: datetime
    estado_actual: EstadoPedidoResponse
    forma_pago: FormaPagoResponse
    direccion_entrega: Optional[DireccionResponse] = None
    detalles: Optional[List[DetallePedidoResponse]] = None
    historial_estados: Optional[List[HistorialEstadoResponse]] = None
    
    model_config = ConfigDict(from_attributes=True)