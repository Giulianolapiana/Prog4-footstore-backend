from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.core.security import AuthenticatedUser
from app.modules.auth.repository import UsuarioRepository

def get_current_user(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> AuthenticatedUser:
    
    # 1. Leer el token desde la cookie, NO desde el header
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado. Falla la cookie.")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")

    usuario = UsuarioRepository(session).get_by_email(email)
    if not usuario or usuario.deleted_at is not None or not usuario.is_active:
        raise HTTPException(status_code=401, detail="Usuario no válido o inactivo")

    # Extraemos los códigos de los roles para pasarlos al frontend
    user_roles = [r.codigo for r in usuario.roles] if hasattr(usuario, 'roles') else []

    return AuthenticatedUser(
        id=usuario.id,
        email=usuario.email,
        roles=user_roles,
        is_active=usuario.is_active,
    )

def require_roles(*roles_requeridos: str):
    """Dependency para proteger rutas según el rol (RBAC)"""
    def dependency(current_user: Annotated[AuthenticatedUser, Depends(get_current_user)]) -> AuthenticatedUser:
        user_roles = set(current_user.roles)
        # Chequea si el usuario tiene al menos uno de los roles requeridos
        if not user_roles.intersection(set(roles_requeridos)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permisos insuficientes. Se requiere alguno de: {roles_requeridos}"
            )
        return current_user
    return dependency
