# app/modules/admin/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class UsuarioAdminUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    is_active: Optional[bool] = None

class AsignarRolesRequest(BaseModel):
    # Recibe una lista de códigos, ej: ["ADMIN", "PEDIDOS"]
    roles_codigos: List[str]