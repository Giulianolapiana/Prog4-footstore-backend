import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
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
