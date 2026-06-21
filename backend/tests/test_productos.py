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

def test_crear_producto_con_ingredientes(client: TestClient, admin_cookies: dict, db_session: Session):
    from app.modules.ingredientes.models import Ingrediente
    unidad = db_session.exec(select(UnidadMedida).where(UnidadMedida.simbolo == "ud")).first()
    categoria = db_session.exec(select(Categoria)).first()
    
    # Crear un ingrediente de prueba
    ingrediente = Ingrediente(nombre="Tomate", es_alergeno=False)
    db_session.add(ingrediente)
    db_session.commit()
    db_session.refresh(ingrediente)
    
    response = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Pizza Especial",
            "descripcion": "Pizza con tomate",
            "precio_base": 5000.0,
            "stock_cantidad": 10,
            "unidad_venta_id": unidad.id,
            "categoria_ids": [categoria.id],
            "ingredientes": [
                {
                    "ingrediente_id": ingrediente.id,
                    "es_removible": True,
                    "es_opcional": False,
                    "cantidad": 150.5,
                    "unidad_medida_id": unidad.id
                }
            ]
        },
        cookies=admin_cookies
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Pizza Especial"
    assert len(data["producto_ingredientes"]) == 1
    
    ing = data["producto_ingredientes"][0]
    assert ing["cantidad"] == "150.500" # JSON serialization makes it a string with 3 decimals
    assert ing["unidad_medida"]["id"] == unidad.id
    assert ing["ingrediente"]["nombre"] == "Tomate"
