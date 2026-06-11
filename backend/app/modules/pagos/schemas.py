# app/modules/pagos/schemas.py
from typing import Optional
from sqlmodel import SQLModel, Field

class CrearPagoRequest(SQLModel):
    """Body que envía el frontend para iniciar un flujo de pago."""
    pedido_id: int = Field(..., description="ID del pedido a pagar")

class ConfirmarPagoRequest(SQLModel):
    """Body para consultar/confirmar el estado de un pago de forma manual."""
    pedido_id: int = Field(..., description="ID del pedido")
    payment_id: Optional[int] = Field(default=None, description="ID del pago en MP")

class PagoCrearResponse(SQLModel):
    """Respuesta con los datos necesarios para levantar el Checkout PRO en el cliente."""
    pago_id: int
    preference_id: str
    init_point: Optional[str] = None
    public_key: Optional[str] = None

class PagoEstadoResponse(SQLModel):
    """Respuesta compacta con el estado actual del cobro."""
    estado: Optional[str] = None  # "pendiente" | "aprobado" | "rechazado"
    pedido_id: int