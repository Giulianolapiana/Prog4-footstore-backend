from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.security import AuthenticatedUser
from app.modules.auth.dependencies import get_current_user
from app.modules.direcciones.schemas import DireccionCreate, DireccionResponse
from app.modules.direcciones.service import DireccionService

router = APIRouter(prefix="/direcciones", tags=["Direcciones de Entrega"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]

def get_direccion_service(session: SessionDep) -> DireccionService:
    return DireccionService(session)

@router.get("/", response_model=list[DireccionResponse])
def listar_direcciones(
    current_user: CurrentUser, 
    svc: DireccionService = Depends(get_direccion_service)
):
    """Devuelve todas las direcciones del usuario logueado."""
    return svc.listar_mis_direcciones(current_user.id)

@router.post("/", response_model=DireccionResponse, status_code=status.HTTP_201_CREATED)
def crear_direccion(
    data: DireccionCreate, 
    current_user: CurrentUser, 
    svc: DireccionService = Depends(get_direccion_service)
):
    return svc.crear(current_user.id, data)

@router.patch("/{id}/principal", response_model=DireccionResponse)
def marcar_como_principal(
    id: int, 
    current_user: CurrentUser, 
    svc: DireccionService = Depends(get_direccion_service)
):
    """Marca una dirección como principal y desmarca el resto de ese usuario."""
    return svc.marcar_principal(id, current_user.id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_direccion(
    id: int, 
    current_user: CurrentUser, 
    svc: DireccionService = Depends(get_direccion_service)
):
    """Realiza un Soft Delete de la dirección del usuario."""
    svc.eliminar(id, current_user.id)