from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.security import AuthenticatedUser, set_auth_cookie, clear_auth_cookie
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import UsuarioCreate, LoginRequest, UsuarioResponse
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticación"])

SessionDep = Annotated[Session, Depends(get_session)]

def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)

# ...
@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(data: UsuarioCreate, svc: AuthService = Depends(get_auth_service)):
    return svc.register(data)

@router.post("/login", response_model=UsuarioResponse)
def login(data: LoginRequest, response: Response, svc: AuthService = Depends(get_auth_service)):
    usuario, token = svc.login(data)
    set_auth_cookie(response, token)  # Inyección de cookie httpOnly
    return usuario

@router.post("/logout")
def logout(response: Response):
    clear_auth_cookie(response)
    return {"detail": "Sesión cerrada correctamente"}

@router.get("/me", response_model=UsuarioResponse)
def get_me(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)], 
    session: SessionDep
):
    from app.modules.auth.repository import UsuarioRepository
    # Buscamos la entidad completa con sus relaciones (roles mapeados) para retornar al cliente
    usuario = UsuarioRepository(session).get_by_id(current_user.id)
    return usuario