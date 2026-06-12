import uuid
import logging
import mercadopago
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlmodel import Session

from app.core.config import settings
from app.modules.pedidos.models import Pedido, HistorialEstadoPedido
from app.modules.pagos.models import Pago
from app.modules.pagos.schemas import PagoCrearResponse, PagoEstadoResponse
from app.modules.pagos.unit_of_work import PagoUnitOfWork

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self, session: Session) -> None:
        self._session = session

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║  MÉTODOS PRIVADOS: COMUNICACIÓN CON EL SDK DE MERCADOPAGO        ║
    # ╚════════════════════════════════════════════════════════════════════╝

    def _get_mp_access_token(self) -> Optional[str]:
        return settings.MP_ACCESS_TOKEN

    def _get_mp_public_key(self) -> Optional[str]:
        return settings.MP_PUBLIC_KEY

    def _crear_preferencia_mp(self, monto: float, titulo: str, pedido_id: int, back_urls: dict) -> dict:
        access_token = self._get_mp_access_token()
        if not access_token:
            raise RuntimeError("MercadoPago no está configurado. Configure MP_ACCESS_TOKEN")

        try:
            sdk = mercadopago.SDK(access_token)

            preference_data = {
                "items": [{
                    "title": titulo,
                    "quantity": 1,
                    "unit_price": float(monto),
                    "currency_id": "ARS",
                }],
                "external_reference": str(pedido_id),
                "back_urls": back_urls,
                "notification_url": (
                    settings.MP_WEBHOOK_URL
                    or f"{settings.VITE_API_URL}/api/v1/pagos/webhook"
                ),
                "auto_return": "approved",
            }

            result = sdk.preference().create(preference_data)

            if result.get("status") not in (200, 201):
                logger.error("Error creando preferencia MP: %s", result)
                raise RuntimeError(f"Error al crear preferencia: {result.get('response', {}).get('message', 'desconocido')}")

            response = result.get("response", {})
            return {
                "preference_id": response.get("id"),
                "init_point": response.get("init_point"),
            }
        except Exception as e:
            logger.exception("Error inesperado al crear preferencia MP")
            raise RuntimeError(f"Error de conexión con MP: {str(e)}")

    def _consultar_pago_mp(self, payment_id: int) -> dict:
        access_token = self._get_mp_access_token()
        if not access_token:
            raise RuntimeError("MP no configurado")

        try:
            sdk = mercadopago.SDK(access_token)
            result = sdk.payment().get(payment_id)

            if result.get("status") != 200:
                logger.error("Error consultando pago MP %s: %s", payment_id, result)
                raise RuntimeError(f"Error al consultar pago {payment_id}")

            response = result.get("response", {})
            return {
                "mp_payment_id": response.get("id"),
                "mp_status": response.get("status"),
                "mp_status_detail": response.get("status_detail"),
                "mp_merchant_order_id": response.get("merchant_order_id"),
            }
        except Exception as e:
            logger.exception("Error consultando pago MP %s", payment_id)
            raise RuntimeError(f"Error de conexión con MP: {str(e)}")

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║  MÉTODOS PÚBLICOS: LÓGICA DEL NEGOCIO LOCAL Y TRANSACTONAL         ║
    # ╚════════════════════════════════════════════════════════════════════╝

    def crear_pago(self, pedido_id: int) -> PagoCrearResponse:
        pedido = self._session.get(Pedido, pedido_id)
        if not pedido:
            raise ValueError("Pedido no encontrado")

        if not self._get_mp_access_token():
            raise ValueError("MercadoPago no configurado.")

        ngrok_url = settings.NGROK_URL or "http://localhost:8000"
        back_urls = {
            "success": f"{ngrok_url}/api/v1/pagos/redirect/{pedido_id}/success",
            "failure": f"{ngrok_url}/api/v1/pagos/redirect/{pedido_id}/failure",
            "pending": f"{ngrok_url}/api/v1/pagos/redirect/{pedido_id}/pending",
        }

        
        mp_data = self._crear_preferencia_mp(
            monto=pedido.total,
            titulo=f"Pedido #{pedido_id} - FoodStore",
            pedido_id=pedido_id,
            back_urls=back_urls,
        )

        with PagoUnitOfWork(self._session) as uow:
            pago = Pago(
                pedido_id=pedido_id,
                monto=pedido.total,
                estado="pendiente",
                mp_preference_id=mp_data["preference_id"],
                mp_init_point=mp_data.get("init_point"),
                idempotency_key=str(uuid.uuid4()),
            )
            uow.pagos.add(pago)
            uow.flush() # Importante para obtener el ID asignado por la BD

            return PagoCrearResponse(
                pago_id=pago.id,
                preference_id=mp_data["preference_id"],
                init_point=mp_data.get("init_point"),
                public_key=self._get_mp_public_key(),
            )

    def procesar_webhook(self, data: dict, query_params: Optional[dict] = None) -> Tuple[dict, Optional[int]]:
        logger.info("Webhook recibido: data=%s qs=%s", data, query_params or {})

        if not data and query_params:
            data = query_params

        topic = data.get("type") or data.get("topic")
        data_id = data.get("data_id") or (data.get("data") or {}).get("id")
        payment_id = data.get("id")

        if not data_id and query_params:
            data_id = query_params.get("data.id") or query_params.get("id")
        if not topic and query_params:
            topic = query_params.get("topic") or query_params.get("type")

        pago_mp_id = payment_id or data_id

        if not pago_mp_id:
            return {"status": "ignored", "reason": "No payment ID"}, None

        if topic not in (None, "payment", "merchant_order"):
            return {"status": "ignored", "reason": f"Topic: {topic}"}, None

        try:
            mp_info = self._consultar_pago_mp(int(pago_mp_id))
            estado_mp = mp_info.get("mp_status")

            if estado_mp == "approved":
                nuevo_estado = "aprobado"
            elif estado_mp in ("rejected", "cancelled", "refunded", "charged_back"):
                nuevo_estado = "rechazado"
            elif estado_mp in ("pending", "in_process", "authorized"):
                nuevo_estado = "pendiente"
            else:
                return {"status": "ignored", "reason": f"Unknown status: {estado_mp}"}, None

            with PagoUnitOfWork(self._session) as uow:
                pago = uow.pagos.get_by_mp_payment_id(int(pago_mp_id))
                
                if not pago and mp_info.get("mp_merchant_order_id"):
                    pago = uow.pagos.get_by_mp_merchant_order_id(mp_info["mp_merchant_order_id"])

                if not pago:
                    return {"status": "ignored", "reason": "Pago not found in local DB"}, None

                if pago.estado != "pendiente":
                    return {"status": "already_processed", "estado": pago.estado}, None

                pago.mp_payment_id = int(pago_mp_id)
                pago.mp_status = estado_mp
                pago.mp_status_detail = mp_info.get("mp_status_detail")
                pago.mp_merchant_order_id = mp_info.get("mp_merchant_order_id")
                pago.estado = nuevo_estado
                pago.updated_at = datetime.now(timezone.utc)
                uow.pagos.update(pago)

                # Si el pago se aprobó, actualizamos el estado del pedido y el historial (FSM v7)
                if nuevo_estado == "aprobado":
                    self._confirmar_pedido_fsm(uow, pago.pedido_id)

            return {
                "status": "processed",
                "pago_id": pago.id,
                "estado": nuevo_estado,
                "pedido_id": pago.pedido_id,
            }, pago.pedido_id

        except Exception as e:
            logger.exception("Error procesando webhook MP")
            return {"status": "error", "reason": str(e)}, None

    def confirmar_pago(self, pedido_id: int, payment_id: Optional[int] = None) -> Tuple[PagoEstadoResponse, Optional[int]]:
        pedido = self._session.get(Pedido, pedido_id)
        if not pedido:
            raise ValueError("Pedido no encontrado")

        resolved_payment_id = payment_id
        if not resolved_payment_id:
            with PagoUnitOfWork(self._session) as uow:
                pago_local = uow.pagos.get_ultimo_by_pedido(pedido_id)
                if pago_local and pago_local.mp_payment_id:
                    resolved_payment_id = pago_local.mp_payment_id

        if resolved_payment_id:
            mp_info = self._consultar_pago_mp(resolved_payment_id)

            estado_mp = mp_info.get("mp_status")
            if estado_mp == "approved":
                nuevo_estado = "aprobado"
            elif estado_mp in ("rejected", "cancelled", "refunded", "charged_back"):
                nuevo_estado = "rechazado"
            else:
                nuevo_estado = "pendiente"

            with PagoUnitOfWork(self._session) as uow:
                pago = uow.pagos.get_by_mp_payment_id(resolved_payment_id)
                if not pago:
                    pago = uow.pagos.get_ultimo_by_pedido(pedido_id)

                if pago:
                    pago.mp_payment_id = resolved_payment_id
                    pago.mp_status = estado_mp
                    pago.mp_status_detail = mp_info.get("mp_status_detail")
                    pago.mp_merchant_order_id = mp_info.get("mp_merchant_order_id")
                    pago.estado = nuevo_estado
                    pago.updated_at = datetime.now(timezone.utc)
                    uow.pagos.update(pago)

                    if nuevo_estado == "aprobado":
                        self._confirmar_pedido_fsm(uow, pedido_id)

            return PagoEstadoResponse(estado=nuevo_estado, pedido_id=pedido_id), pedido_id

        # Si llegamos acá es porque no hay payment_id ni en la BD ni en el request
        with PagoUnitOfWork(self._session) as uow:
            pago_local = uow.pagos.get_ultimo_by_pedido(pedido_id)
            return PagoEstadoResponse(
                estado=pago_local.estado if pago_local else None,
                pedido_id=pedido_id,
            ), None

    def _confirmar_pedido_fsm(self, uow: PagoUnitOfWork, pedido_id: int):
        """
        Sincroniza el pedido al estado 'CONFIRMADO' (Reglas de Negocio FSM v7)
        y agrega el registro en el historial de auditoría de forma atómica.
        """
        pedido = uow.pedidos.get_by_id(pedido_id)
        if not pedido:
            return

        # Para evitar transiciones duplicadas si el webhook de MP llega dos veces
        estado_actual = uow.estados.get_by_id(pedido.estado_actual_id)
        if estado_actual and estado_actual.codigo == "CONFIRMADO":
            return

        estado_confirmado = uow.estados.get_by_codigo("CONFIRMADO")
        if estado_confirmado:
            # 1. Actualiza la cabecera
            pedido.estado_actual_id = estado_confirmado.id
            pedido.updated_at = datetime.now(timezone.utc)
            uow.pedidos.update(pedido)

            # 2. Audit trail append-only (Obligatorio en v6.0)
            uow.historiales.add(HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_id=estado_confirmado.id,
                # Asumimos que el usuario que realizó la acción original es el dueño
                # o pasamos None porque fue una acción automatizada del sistema.
                usuario_id=pedido.usuario_id 
            ))