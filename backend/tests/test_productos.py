import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.modules.productos.models import Producto, UnidadMedida
from app.modules.categorias.models import Categoria

def test_listar_productos_vacios(client: TestClient):
    response = client.get("/api/v1/productos")
    assert response.status_code == 200
    assert response.json()["items"] == []

def test_crear_producto_auth_required(client: TestClient):
    response = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Hamburguesa Test",
            "descripcion": "Rica",
            "precio_base": 1500.0,
            "stock_cantidad": 10
        }
    )
    assert response.status_code == 401

def test_crear_y_listar_producto_admin(client: TestClient, admin_cookies: dict, db_session: Session):
    unidad = db_session.exec(select(UnidadMedida).where(UnidadMedida.simbolo == "ud")).first()
    categoria = db_session.exec(select(Categoria)).first()
    
    response = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Hamburguesa Test",
            "descripcion": "Rica",
            "precio_base": 1500.0,
            "stock_cantidad": 10,
            "unidad_venta_id": unidad.id,
            "categoria_ids": [categoria.id],
            "imagenes_url": ["http://test.com/img.jpg"]
        },
        cookies=admin_cookies
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Hamburguesa Test"
    
    res_list = client.get("/api/v1/productos")
    assert res_list.status_code == 200
    assert len(res_list.json()["items"]) == 1
    assert res_list.json()["items"][0]["id"] == data["id"]
