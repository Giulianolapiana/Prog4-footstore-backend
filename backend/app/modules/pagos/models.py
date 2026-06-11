# app/modules/pagos/models.py
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from sqlalchemy import BigInteger

class Pago(SQLModel, table=True):
    """Modelo que representa un pago asociado a un pedido, incluyendo datos de MercadoPago."""
    __tablename__ = "pagos"

    # ── Datos locales del pago ──────────────────────────────────────────────
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", index=True)
    monto: float = Field(ge=0)

    # Estado local: "pendiente" | "aprobado" | "rechazado"
    estado: str = Field(max_length=20)

    # ── Datos de la PREFERENCIA (Etapa 1 del flujo) ──────────────────────────
    mp_preference_id: Optional[str] = Field(default=None, max_length=255)
    mp_init_point: Optional[str] = Field(default=None, max_length=500)

    # ── Datos del PAGO REAL (Etapa de Webhook / Notificación) ──────────────────
    mp_payment_id: Optional[int] = Field(default=None, sa_type=BigInteger)
    mp_merchant_order_id: Optional[int] = Field(default=None, sa_type=BigInteger)
    mp_status: Optional[str] = Field(default=None, max_length=50)
    mp_status_detail: Optional[str] = Field(default=None, max_length=100)

    # ── Control de idempotencia ──────────────────────────────────────────────
    idempotency_key: str = Field(max_length=36, unique=True)

    # ── Timestamps ───────────────────────────────────────────────────────────
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)