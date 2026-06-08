from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from app.core.base_model import BaseEntity

#agregar direcciones: list["DireccionEntrega"] = Relationship(back_populates="usuario") dentro de la clase Usuario para que quede bien linkeado).

class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_rol"
    usuario_id: int = Field(foreign_key="usuario.id", primary_key=True)
    rol_id: int = Field(foreign_key="rol.id", primary_key=True)

class Rol(SQLModel, table=True):
    __tablename__ = "rol"
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True)  # ADMIN, STOCK, PEDIDOS, CLIENT
    nombre: str

    usuarios: list["Usuario"] = Relationship(
        back_populates="roles",
        link_model=UsuarioRol,
    )

class Usuario(BaseEntity, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False, max_length=255)
    hashed_password: str = Field(nullable=False, max_length=255)
    nombre: str = Field(nullable=False, max_length=100)
    apellido: str = Field(nullable=False, max_length=100)
    is_active: bool = Field(default=True, nullable=False)

    roles: list[Rol] = Relationship(
        back_populates="usuarios",
        link_model=UsuarioRol,
    )

    direcciones: list["DireccionEntrega"] = Relationship(back_populates="usuario")