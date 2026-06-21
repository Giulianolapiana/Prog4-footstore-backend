import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
<<<<<<< HEAD
from app.modules.auth.models import Usuario, Rol, UsuarioRol
from app.modules.productos.models import Producto
from app.modules.direcciones.models import DireccionEntrega
from app.modules.pedidos.models import FormaPago, Pedido, HistorialEstadoPedido

def setup_user_and_data(client: TestClient, session: Session):
    # Register
    client.post("/api/v1/auth/register", json={
        "email": "cliente@test.com", "password": "Pass", "nombre": "C", "apellido": "C"
    })
    # Login
    client.post("/api/v1/auth/login", json={"email": "cliente@test.com", "password": "Pass"})
    
    user = session.exec(select(Usuario).where(Usuario.email == "cliente@test.com")).first()
    
    # Create product
    producto = Producto(nombre="Papas", precio_base=500.0, stock_cantidad=20, disponible=True)
    session.add(producto)
    
    # Create direccion
    direccion = DireccionEntrega(usuario_id=user.id, calle="Fake St", numero="123", ciudad="City")
    session.add(direccion)
    
    session.commit()
    session.refresh(producto)
    session.refresh(direccion)
    
    forma_pago = session.exec(select(FormaPago).where(FormaPago.codigo == "CASH")).first()
    
    return {
        "usuario_id": user.id,
        "producto_id": producto.id,
        "direccion_id": direccion.id,
        "forma_pago_id": forma_pago.id
    }

def test_crear_y_cancelar_pedido(client: TestClient, session: Session):
    data = setup_user_and_data(client, session)
    
    # Crear pedido
    res_crear = client.post(
        "/api/v1/pedidos/",
        json={
            "direccion_entrega_id": data["direccion_id"],
            "forma_pago_id": data["forma_pago_id"],
            "detalles": [
                {
                    "producto_id": data["producto_id"],
                    "cantidad": 2
                }
            ]
        }
    )
    assert res_crear.status_code == 201, res_crear.text
    pedido_id = res_crear.json()["id"]
    
    # Check historial
    historial_inicial = session.exec(select(HistorialEstadoPedido).where(HistorialEstadoPedido.pedido_id == pedido_id)).all()
    assert len(historial_inicial) == 1
    assert historial_inicial[0].estado_desde is None
    assert historial_inicial[0].estado_hacia == "PENDIENTE"
    
    # Cancelar pedido con motivo
    res_cancelar = client.patch(
        f"/api/v1/pedidos/{pedido_id}/cancelar",
        json={"motivo": "Me arrepentí"}
    )
    assert res_cancelar.status_code == 200, res_cancelar.text
    data_cancelado = res_cancelar.json()
    assert data_cancelado["estado_actual"]["codigo"] == "CANCELADO"
    assert data_cancelado["motivo_cancelacion"] == "Me arrepentí"
    
    # Verificar que el stock se haya devuelto
    producto = session.get(Producto, data["producto_id"])
    assert producto.stock_cantidad == 20 # Originalmente era 20, bajó a 18 al crear, y subió a 20 al cancelar
=======
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
    assert data["total"] == 1050.0
    
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
>>>>>>> 703097aacb41fffe9f47a46130a99dbb10ef5027
