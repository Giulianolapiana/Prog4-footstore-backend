import logging
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.core.ws_manager import ws_manager
from app.modules.pagos.schemas import (
    CrearPagoRequest,
    ConfirmarPagoRequest,
    PagoCrearResponse,
    PagoEstadoResponse,
)
from app.modules.pagos.models import Pago
from app.modules.pagos.service import PaymentService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pagos", tags=["Pasarela MercadoPago"])

def get_payment_service(session: Session = Depends(get_session)) -> PaymentService:
    return PaymentService(session)

@router.post("/create-preference", response_model=PagoCrearResponse, status_code=status.HTTP_201_CREATED)
def create_preference(
    data: CrearPagoRequest,
    svc: PaymentService = Depends(get_payment_service),
):
    return svc.crear_pago(data.pedido_id)

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

@router.get("/redirect/{pedido_id}/{status_mp}")
async def redirect_after_pago(pedido_id: int, status_mp: str, request: Request):
    frontend_url = settings.VITE_FRONTEND_URL or "http://localhost:5174" # Puerto del Store público
    qs = request.url.query
    url = f"{frontend_url}/orders/{pedido_id}/{status_mp}"
    if qs:
        url += f"?{qs}"
    return RedirectResponse(url=url)