import logging
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.core.websocket import ws_manager
from app.modules.pagos.schemas import (
    CrearPagoRequest,
    ConfirmarPagoRequest,
    PagoCrearResponse,
    PagoEstadoResponse,
)
from app.modules.pagos.models import Pago
from app.modules.pagos.service import PaymentService
from fastapi import HTTPException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pagos", tags=["Pasarela MercadoPago"])

def get_payment_service(session: Session = Depends(get_session)) -> PaymentService:
    return PaymentService(session)

@router.post("/create-preference", response_model=PagoCrearResponse, status_code=status.HTTP_201_CREATED)
def create_preference(
    data: CrearPagoRequest,
    svc: PaymentService = Depends(get_payment_service),
):
    try:
        return svc.crear_pago(data.pedido_id)
    except ValueError as e:
        if "no encontrado" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        # Errores de la SDK de MP
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/webhook")
async def webhook(
    request: Request,
    svc: PaymentService = Depends(get_payment_service),
):
    try:
        query_params = dict(request.query_params)
        if request.headers.get("content-type", "").startswith("application/json"):
            data = await request.json()
        else:
            data = dict(await request.form())
            
        res, pedido_id = svc.procesar_webhook(data, query_params=query_params)
        
        # Si el webhook procesó con éxito un aprobado, alertamos reactivamente por WS
        if res.get("status") == "processed" and res.get("estado") == "aprobado" and pedido_id:
            await ws_manager.broadcast_pedido_update(
                pedido_id=pedido_id,
                usuario_id=None, # Origen sistema (IPN)
                evento="pago_confirmado",
                estado_nuevo="CONFIRMADO",
                estado_anterior="PENDIENTE"
            )
        return res
    except Exception as e:
        logger.exception("Error en webhook MP")
        return {"status": "error", "reason": str(e)}

@router.post("/confirm", response_model=PagoEstadoResponse)
async def confirm_payment(
    data: ConfirmarPagoRequest,
    svc: PaymentService = Depends(get_payment_service),
):
    try:
        res, pedido_id = svc.confirmar_pago(data.pedido_id, data.payment_id)
        
        if res.estado == "aprobado" and pedido_id:
            await ws_manager.broadcast_pedido_update(
                pedido_id=pedido_id,
                usuario_id=None,
                evento="pago_confirmado",
                estado_nuevo="CONFIRMADO",
                estado_anterior="PENDIENTE"
            )
        return res
    except ValueError as e:
        if "no encontrado" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/redirect/{pedido_id}/{status_mp}")
async def redirect_after_pago(
    pedido_id: int, 
    status_mp: str, 
    request: Request,
    svc: PaymentService = Depends(get_payment_service)
):
    frontend_url = settings.VITE_FRONTEND_URL
    qs = request.url.query
    
    # Mapeo de estados de MercadoPago a los estados del frontend
    status_map = {
        "success": "exito",
        "failure": "error",
        "pending": "pendiente"
    }
    front_status = status_map.get(status_mp, "error")

    # Si el pago falló o fue cancelado por el usuario, cancelamos el pedido para liberar stock
    if status_mp == "failure":
        try:
            from app.modules.pedidos.service import PedidoService
            pedido_svc = PedidoService(svc._session)
            pedido_svc.cancelar_pedido(pedido_id=pedido_id, usuario_id=None, es_cliente=False)
            
            # Avisamos por WS que se canceló
            await ws_manager.broadcast_pedido_update(
                pedido_id=pedido_id,
                usuario_id=None,
                evento="estado_cambiado",
                estado_nuevo="CANCELADO",
                estado_anterior="PENDIENTE"
            )
        except Exception as e:
            logger.error(f"Error al auto-cancelar el pedido fallido {pedido_id}: {e}")
    
    url = f"{frontend_url}/pago/{front_status}"
    
    # Asegurar que external_reference esté presente para la confirmación proactiva
    if qs:
        if "external_reference" not in qs:
            url += f"?{qs}&external_reference={pedido_id}"
        else:
            url += f"?{qs}"
    else:
        url += f"?external_reference={pedido_id}"
        
    return RedirectResponse(url=url)