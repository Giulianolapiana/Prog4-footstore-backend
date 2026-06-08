# app/modules/admin/router.py
from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, Query, Path, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.security import AuthenticatedUser
from app.modules.auth.dependencies import require_roles, get_current_user
from app.modules.auth.schemas import UsuarioResponse
from app.modules.admin.schemas import UsuarioAdminUpdate, AsignarRolesRequest
from app.modules.admin.service import AdminService

# Todas las dependencias de este router exigen rol ADMIN
router = APIRouter(
    prefix="/admin/usuarios", 
    tags=["Panel de Administración"],
    dependencies=[Depends(require_roles("ADMIN"))]
)

SessionDep = Annotated[Session, Depends(get_session)]

def get_admin_service(session: SessionDep) -> AdminService:
    return AdminService(session)

@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    rol: Annotated[Optional[str], Query(description="Filtrar por código de rol")] = None,
    svc: AdminService = Depends(get_admin_service)
):
    return svc.listar_usuarios(skip=skip, limit=limit, rol_codigo=rol)

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(
    usuario_id: Annotated[int, Path(ge=1)],
    data: UsuarioAdminUpdate,
    svc: AdminService = Depends(get_admin_service)
):
    return svc.actualizar_usuario(usuario_id, data)

@router.post("/{usuario_id}/roles", response_model=UsuarioResponse)
def asignar_roles(
    usuario_id: Annotated[int, Path(ge=1)],
    data: AsignarRolesRequest,
    svc: AdminService = Depends(get_admin_service)
):
    """Permite al administrador cambiarle los roles a un usuario (ej: ascender a empleado)."""
    return svc.asignar_roles(usuario_id, data)

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    usuario_id: Annotated[int, Path(ge=1)],
    svc: AdminService = Depends(get_admin_service)
):
    svc.soft_delete_usuario(usuario_id)