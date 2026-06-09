# app/modules/admin/router.py
from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
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
    try:
        return svc.actualizar_usuario(usuario_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{usuario_id}/roles", response_model=UsuarioResponse)
def asignar_roles(
    usuario_id: Annotated[int, Path(ge=1)],
    data: AsignarRolesRequest,
    svc: AdminService = Depends(get_admin_service)
):
    """Permite al administrador cambiarle los roles a un usuario (ej: ascender a empleado)."""
    try:
        return svc.asignar_roles(usuario_id, data)
    except ValueError as e:
        # El service distingue 404 (usuario no encontrado) de 400 (rol inválido / sin roles)
        # Si el mensaje menciona "no encontrado" → 404, de lo contrario → 400
        if "no encontrado" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    usuario_id: Annotated[int, Path(ge=1)],
    svc: AdminService = Depends(get_admin_service)
):
    try:
        svc.soft_delete_usuario(usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))