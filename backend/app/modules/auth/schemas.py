from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional

class RolResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    model_config = ConfigDict(from_attributes=True)

class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str
    apellido: str

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UsuarioResponse(UsuarioBase):
    id: int
    is_active: bool
    roles: list[RolResponse]
    model_config = ConfigDict(from_attributes=True)