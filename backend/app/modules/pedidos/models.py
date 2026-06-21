# app/modules/pedidos/models.py
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship
from app.core.base_model import BaseEntity
from decimal import Decimal
from sqlalchemy import Column, DECIMAL

if TYPE_CHECKING:
    from app.modules.auth.models import Usuario
    from app.modules.direcciones.models import DireccionEntrega
    from app.modules.productos.models import Producto

class EstadoPedido(SQLModel, table=True):
    __tablename__ = "estado_pedido"
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True) # PENDIENTE, CONFIRMADO, etc.
    nombre: str

class FormaPago(SQLModel, table=True):
    __tablename__ = "forma_pago"
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True) # CASH, MP, CREDIT, DEBIT
    nombre: str

class HistorialEstadoPedido(SQLModel, table=True):
    """
    Audit Trail Append-Only: 
    Solo INSERTs, jamás UPDATE ni DELETE. No hereda de BaseEntity.
    """
    __tablename__ = "historial_estado_pedido"
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    estado_desde: Optional[str] = Field(default=None, foreign_key="estado_pedido.codigo")
    estado_hacia: str = Field(foreign_key="estado_pedido.codigo")
    usuario_id: int = Field(foreign_key="usuario.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    pedido: "Pedido" = Relationship(back_populates="historial_estados")

class DetallePedido(BaseEntity, table=True):
    __tablename__ = "detalle_pedido"
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    producto_id: int = Field(foreign_key="producto.id")
    
    # Snapshot Pattern — inmutables
    nombre_snapshot: str = Field(nullable=False)
    precio_snapshot: Decimal = Field(sa_column=Column(DECIMAL(10, 2), nullable=False), ge=0)
    
    cantidad: int = Field(nullable=False, gt=0)
    subtotal_snap: Decimal = Field(sa_column=Column(DECIMAL(10, 2), nullable=False), ge=0)

    pedido: "Pedido" = Relationship(back_populates="detalles")
    producto: "Producto" = Relationship()

class Pedido(BaseEntity, table=True):
    __tablename__ = "pedido"
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    estado_actual_id: int = Field(foreign_key="estado_pedido.id")
    forma_pago_id: int = Field(foreign_key="forma_pago.id")
    direccion_entrega_id: int = Field(foreign_key="direccion_entrega.id")
    subtotal: Decimal = Field(sa_column=Column(DECIMAL(10, 2), nullable=False), ge=0)
    descuento: Decimal = Field(sa_column=Column(DECIMAL(10, 2), default=0.00), ge=0)
    costo_envio: Decimal = Field(sa_column=Column(DECIMAL(10, 2), default=50.00), ge=0)
    total: Decimal = Field(sa_column=Column(DECIMAL(10, 2), nullable=False), ge=0)

    # Relaciones
    usuario: "Usuario" = Relationship()
    estado_actual: EstadoPedido = Relationship()
    forma_pago: FormaPago = Relationship()
    direccion_entrega: "DireccionEntrega" = Relationship()
    
    detalles: List[DetallePedido] = Relationship(back_populates="pedido")
    historial_estados: List[HistorialEstadoPedido] = Relationship(back_populates="pedido")
