import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.modules.pedidos.models import Pedido, HistorialEstadoPedido

from app.modules.pedidos.models import FormaPago
from app.modules.direcciones.models import DireccionEntrega

def test_crear_pedido(client: TestClient, db_session: Session, client_cookies: dict, producto_factory):
    producto = producto_factory(nombre="Papas Test", precio=500.0, stock=20)
    forma = db_session.exec(select(FormaPago).where(FormaPago.codigo == "EFECTIVO")).first()
    direccion = db_session.exec(select(DireccionEntrega)).first()
    
    res = client.post(
        "/api/v1/pedidos/",
        json={
            "forma_pago_id": forma.id,
            "direccion_entrega_id": direccion.id,
            "detalles": [
                {
                    "producto_id": producto.id,
                    "cantidad": 2
                }
            ]
        },
        cookies=client_cookies
    )
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["total"] == 1000.0
    
    db_session.refresh(producto)
    assert producto.stock_cantidad == 18

    # Historial de inicio
    historial = db_session.exec(select(HistorialEstadoPedido).where(HistorialEstadoPedido.pedido_id == data["id"])).all()
    assert len(historial) == 1
    assert historial[0].estado_desde is None
    assert historial[0].estado_hacia == "PENDIENTE"

def test_fsm_avanzar_estado(client: TestClient, admin_cookies: dict, pedido_factory):
    pedido_data = pedido_factory()
    pedido_id = pedido_data["id"]

    # 1. PENDIENTE -> CONFIRMADO
    res = client.patch(f"/api/v1/pedidos/{pedido_id}/estado", json={"estado_codigo": "CONFIRMADO"}, cookies=admin_cookies)
    assert res.status_code == 200, res.text
    
    # 2. CONFIRMADO -> EN_PREP
    res = client.patch(f"/api/v1/pedidos/{pedido_id}/estado", json={"estado_codigo": "EN_PREP"}, cookies=admin_cookies)
    assert res.status_code == 200
    
    # 3. EN_PREP -> ENTREGADO
    res = client.patch(f"/api/v1/pedidos/{pedido_id}/estado", json={"estado_codigo": "ENTREGADO"}, cookies=admin_cookies)
    assert res.status_code == 200

    # 4. Una vez entregado no se puede transicionar
    res_err = client.patch(f"/api/v1/pedidos/{pedido_id}/estado", json={"estado_codigo": "CANCELADO"}, cookies=admin_cookies)
    assert res_err.status_code == 400

def test_cancelar_pedido_propio(client: TestClient, client_cookies: dict, pedido_factory):
    pedido = pedido_factory()
    res = client.patch(f"/api/v1/pedidos/{pedido['id']}/cancelar", json={}, cookies=client_cookies)
    assert res.status_code == 200
    assert res.json()["estado_actual"]["codigo"] == "CANCELADO"
