import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.modules.pedidos.models import Pedido

def test_crear_pago(client: TestClient, client_cookies: dict, pedido_factory):
    pedido_data = pedido_factory()
    
    with patch("app.modules.pagos.service.PaymentService._crear_preferencia_mp") as mock_mp:
        mock_mp.return_value = {
            "preference_id": "test_pref_id",
            "init_point": "http://sandbox.mp/123"
        }
        res = client.post(
            "/api/v1/pagos/create-preference", 
            json={"pedido_id": pedido_data['id']},
            cookies=client_cookies
        )
        assert res.status_code == 201

def test_webhook_mercadopago(client: TestClient, db_session: Session, pedido_factory):
    pedido_data = pedido_factory()
    
    with patch("app.modules.pagos.service.PaymentService._consultar_pago_mp") as mock_mp:
        mock_mp.return_value = {
            "mp_payment_id": 12345,
            "mp_status": "approved",
            "mp_status_detail": "accredited",
            "mp_merchant_order_id": 999,
            "mp_external_reference": str(pedido_data["id"])
        }
        
        res = client.post(
            "/api/v1/pagos/webhook",
            json={"type": "payment", "data": {"id": "12345"}}
        )
        assert res.status_code == 200
