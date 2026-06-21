# app/modules/pedidos/router.py
from typing import List, Annotated
from fastapi import APIRouter, Depends, Query, Path, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.security import AuthenticatedUser
from app.modules.auth.dependencies import require_roles, get_current_user
from app.modules.pedidos.schemas import PedidoCreate, PedidoResponse, AvanzarEstadoRequest
from app.modules.pedidos.service import PedidoService

from fastapi import APIRouter, Depends, Query, Path, status

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]

def get_pedido_service(session: SessionDep) -> PedidoService:
    return PedidoService(session)

@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def crear_pedido(
    data: PedidoCreate,
    current_user: CurrentUser,
    svc: PedidoService = Depends(get_pedido_service),
):
    """Crea un pedido desde el carrito. El usuario logueado queda como dueño."""
    #Ejecuta la lógica de negocio, el commit en la BD, y el WebSocket
    pedido = await svc.crear_pedido(usuario_id=current_user.id, data=data)
    
    return pedido

@router.get("/", response_model=List[PedidoResponse])
def listar_pedidos(
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    svc: PedidoService = Depends(get_pedido_service),
):
    """
    Si es CLIENT, ve solo sus pedidos.
    Si es ADMIN o PEDIDOS, ve los de todos.
    """
    es_gestor = any(rol in ["ADMIN", "PEDIDOS"] for rol in current_user.roles)
    filtro_usuario = None if es_gestor else current_user.id
    
    return svc.listar_pedidos(usuario_id=filtro_usuario, skip=skip, limit=limit)

@router.get("/{pedido_id}", response_model=PedidoResponse)
def detalle_pedido(
    pedido_id: Annotated[int, Path(ge=1)],
    current_user: CurrentUser,
    svc: PedidoService = Depends(get_pedido_service),
):
    es_gestor = any(rol in ["ADMIN", "PEDIDOS"] for rol in current_user.roles)
    return svc.obtener_por_id(pedido_id, current_user.id, es_gestor)

@router.patch("/{pedido_id}/estado", response_model=PedidoResponse)
async def avanzar_estado_pedido(  # ★ Cambiado a async
    pedido_id: Annotated[int, Path(ge=1)],
    data: AvanzarEstadoRequest,
    svc: PedidoService = Depends(get_pedido_service),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN", "PEDIDOS"))
):
    """Solo el personal autorizado puede avanzar"""
    pedido = await svc.avanzar_estado(pedido_id, data.estado_codigo, current_user.id)
    
    return pedido

@router.patch("/{pedido_id}/cancelar", response_model=PedidoResponse)
async def cancelar_pedido(  # ★ Cambiado a async
    pedido_id: Annotated[int, Path(ge=1)],
    current_user: CurrentUser,
    svc: PedidoService = Depends(get_pedido_service),
):
    """
    Permite cancelar el pedido. El cliente solo puede si está PENDIENTE o CONFIRMADO.
    """
    es_cliente = "CLIENT" in current_user.roles and "ADMIN" not in current_user.roles
    
    # Cancela el pedido
    pedido = await svc.cancelar_pedido(pedido_id, current_user.id, es_cliente)
    
    return pedido