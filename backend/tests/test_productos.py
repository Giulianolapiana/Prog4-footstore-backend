import pytest
from fastapi.testclient import TestClient
<<<<<<< HEAD
from sqlmodel import Session
from app.modules.productos.models import Producto
=======
from sqlmodel import Session, select
from app.modules.productos.models import Producto, UnidadMedida
from app.modules.categorias.models import Categoria
>>>>>>> 703097aacb41fffe9f47a46130a99dbb10ef5027

def test_listar_productos_vacios(client: TestClient):
    response = client.get("/api/v1/productos")
    assert response.status_code == 200
<<<<<<< HEAD
    assert response.json() == []

def test_crear_producto_auth_required(client: TestClient):
    # Sin autenticar debe fallar
=======
    assert response.json()["items"] == []

def test_crear_producto_auth_required(client: TestClient):
>>>>>>> 703097aacb41fffe9f47a46130a99dbb10ef5027
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

<<<<<<< HEAD
def test_crear_y_listar_producto_admin(client: TestClient, session: Session):
    # 1. Crear un ADMIN y loguearse
    client.post("/api/v1/auth/register", json={
        "email": "admin2@foodstore.com", "password": "Pass", "nombre": "A", "apellido": "A"
    })
    # Le inyectamos el rol ADMIN manualmente en BD
    from app.modules.auth.models import Usuario, Rol, UsuarioRol
    from sqlmodel import select
    admin = session.exec(select(Usuario).where(Usuario.email == "admin2@foodstore.com")).first()
    rol_admin = session.exec(select(Rol).where(Rol.codigo == "ADMIN")).first()
    session.add(UsuarioRol(usuario_id=admin.id, rol_id=rol_admin.id))
    session.commit()
    
    # Login
    client.post("/api/v1/auth/login", json={"email": "admin2@foodstore.com", "password": "Pass"})
    
    # 2. Crear producto
=======
def test_crear_y_listar_producto_admin(client: TestClient, admin_cookies: dict, db_session: Session):
    unidad = db_session.exec(select(UnidadMedida).where(UnidadMedida.simbolo == "ud")).first()
    categoria = db_session.exec(select(Categoria)).first()
    
>>>>>>> 703097aacb41fffe9f47a46130a99dbb10ef5027
    response = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Hamburguesa Test",
            "descripcion": "Rica",
            "precio_base": 1500.0,
<<<<<<< HEAD
            "stock_cantidad": 10
        }
=======
            "stock_cantidad": 10,
            "unidad_venta_id": unidad.id,
            "categoria_ids": [categoria.id],
            "imagenes_url": ["http://test.com/img.jpg"]
        },
        cookies=admin_cookies
>>>>>>> 703097aacb41fffe9f47a46130a99dbb10ef5027
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Hamburguesa Test"
    
<<<<<<< HEAD
    # 3. Listar productos
    res_list = client.get("/api/v1/productos")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1
    assert res_list.json()[0]["id"] == data["id"]
=======
    res_list = client.get("/api/v1/productos")
    assert res_list.status_code == 200
    assert len(res_list.json()["items"]) == 1
    assert res_list.json()["items"][0]["id"] == data["id"]
>>>>>>> 703097aacb41fffe9f47a46130a99dbb10ef5027
