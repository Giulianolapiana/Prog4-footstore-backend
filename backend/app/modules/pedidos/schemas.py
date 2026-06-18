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

from pydantic import BaseModel, ConfigDict, Field

class DetallePedidoResponse(BaseModel):
    id: int
    producto_id: int
    producto_nombre: str = Field(validation_alias="nombre_snapshot")
    producto_precio: float = Field(validation_alias="precio_snapshot")
    cantidad: int
    subtotal: float = Field(validation_alias="subtotal_snap")
    model_config = ConfigDict(from_attributes=True)

class PedidoResponse(BaseModel):
    id: int
    usuario_id: int
    subtotal: float
    descuento: float
    costo_envio: float
    total: float
    created_at: datetime
    estado_actual: EstadoPedidoResponse
    forma_pago: FormaPagoResponse
    direccion_entrega: Optional[DireccionResponse] = None
    detalles: Optional[List[DetallePedidoResponse]] = None
    historial_estados: Optional[List[HistorialEstadoResponse]] = None
    
    model_config = ConfigDict(from_attributes=True)