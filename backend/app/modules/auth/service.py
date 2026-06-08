from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlmodel import Session
from app.core.security import hash_password, verify_password, create_access_token
from app.modules.auth.models import Usuario
from app.modules.auth.schemas import UsuarioCreate, LoginRequest
from app.modules.auth.unit_of_work import AuthUnitOfWork

class AuthService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def register(self, data: UsuarioCreate) -> Usuario:
        with AuthUnitOfWork(self._session) as uow:
            existente = uow.usuarios.get_by_email(data.email)
            if existente and getattr(existente, "deleted_at", None) is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe un usuario activo con el email '{data.email}'."
                )

            # Buscar obligatoriamente el rol por defecto
            rol_client = uow.roles.get_by_codigo("CLIENT")
            if not rol_client:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error de inicialización: El rol CLIENT no se encuentra en la DB."
                )

            # Re-activar usuario si sufrió soft-delete previo
            if existente and getattr(existente, "deleted_at", None) is not None:
                existente.email = data.email
                existente.hashed_password = hash_password(data.password)
                existente.nombre = data.nombre
                existente.apellido = data.apellido
                existente.is_active = True
                existente.deleted_at = None
                existente.updated_at = datetime.now(timezone.utc)
                existente.roles = [rol_client]
                uow.usuarios.add(existente)
                return existente

            usuario = Usuario(
                email=data.email,
                hashed_password=hash_password(data.password),
                nombre=data.nombre,
                apellido=data.apellido,
                is_active=True,
                roles=[rol_client]
            )
            uow.usuarios.add(usuario)
        return usuario

    def login(self, data: LoginRequest) -> tuple[Usuario, str]:
        with AuthUnitOfWork(self._session) as uow:
            usuario = uow.usuarios.get_by_email(data.email)
            if not usuario or getattr(usuario, "deleted_at", None) is not None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales inválidas"
                )
            
            if not verify_password(data.password, usuario.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales inválidas"
                )

            if not usuario.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="El usuario se encuentra deshabilitado"
                )

            token = create_access_token(data={"sub": usuario.email})
            return usuario, token