from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from app.core.base_model import BaseEntity

class DireccionEntrega(BaseEntity, table=True):
    __tablename__ = "direccion_entrega"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    calle: str = Field(nullable=False, max_length=255)
    numero: str = Field(nullable=False, max_length=50)
    piso: Optional[str] = Field(default=None, max_length=50)
    depto: Optional[str] = Field(default=None, max_length=50)
    ciudad: str = Field(nullable=False, max_length=100)
    codigo_postal: Optional[str] = Field(default=None, max_length=50)
    alias: str = Field(nullable=False, max_length=100) # Ej: "Casa", "Trabajo"
    es_principal: bool = Field(default=False, nullable=False)

    usuario: "Usuario" = Relationship(back_populates="direcciones")