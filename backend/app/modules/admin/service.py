# app/modules/admin/service.py
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.auth.models import Usuario, Rol
from app.modules.auth.unit_of_work import AuthUnitOfWork
from app.modules.admin.schemas import UsuarioAdminUpdate, AsignarRolesRequest

class AdminService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def listar_usuarios(self, skip: int = 0, limit: int = 50, rol_codigo: Optional[str] = None) -> List[Usuario]:
        with AuthUnitOfWork(self._session) as uow:
            return uow.usuarios.get_all_with_filters(skip=skip, limit=limit, rol_codigo=rol_codigo)

    def actualizar_usuario(self, usuario_id: int, data: UsuarioAdminUpdate) -> Usuario:
        with AuthUnitOfWork(self._session) as uow:
            usuario = uow.usuarios.get_by_id(usuario_id)
            if not usuario:
                raise HTTPException(status_code=404, detail="Usuario no encontrado.")

            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(usuario, key, value)
            
            uow.usuarios.update(usuario)
            return usuario

    def asignar_roles(self, usuario_id: int, data: AsignarRolesRequest) -> Usuario:
        with AuthUnitOfWork(self._session) as uow:
            usuario = uow.usuarios.get_by_id(usuario_id)
            if not usuario:
                raise HTTPException(status_code=404, detail="Usuario no encontrado.")

            nuevos_roles = []
            for codigo in data.roles_codigos:
                rol_db = uow.roles.get_by_codigo(codigo)
                if not rol_db:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"El rol {codigo} no existe en el sistema."
                    )
                nuevos_roles.append(rol_db)

            if not nuevos_roles:
                raise HTTPException(status_code=400, detail="Debe asignar al menos un rol.")

            # Sobrescribimos los roles viejos por los nuevos
            usuario.roles = nuevos_roles
            uow.usuarios.update(usuario)
            return usuario

    def soft_delete_usuario(self, usuario_id: int) -> None:
        with AuthUnitOfWork(self._session) as uow:
            usuario = uow.usuarios.get_by_id(usuario_id)
            if not usuario:
                raise HTTPException(status_code=404, detail="Usuario no encontrado.")
            
            # Verificamos que no se esté borrando al admin principal por accidente
            if "ADMIN" in [r.codigo for r in usuario.roles] and usuario.id == 1:
                raise HTTPException(
                    status_code=403, 
                    detail="No se puede eliminar al administrador principal del sistema."
                )

            usuario.deleted_at = datetime.now(timezone.utc)
            usuario.is_active = False
            uow.usuarios.update(usuario)