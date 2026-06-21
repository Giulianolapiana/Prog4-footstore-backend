import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.modules.auth.models import Usuario

<<<<<<< HEAD
def test_register_usuario(client: TestClient, session: Session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@foodstore.com",
            "password": "Password123",
            "nombre": "Test",
=======
def test_register_usuario(client: TestClient, db_session: Session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nuevo@foodstore.com",
            "password": "Password123!",
            "nombre": "Nuevo",
>>>>>>> 703097aacb41fffe9f47a46130a99dbb10ef5027
            "apellido": "User"
        }
    )
    assert response.status_code == 201
    data = response.json()
<<<<<<< HEAD
    assert data["email"] == "test@foodstore.com"
    assert data["nombre"] == "Test"
    
    # Check db
    usuario_db = session.exec(select(Usuario).where(Usuario.email == "test@foodstore.com")).first()
=======
    assert data["email"] == "nuevo@foodstore.com"
    
    usuario_db = db_session.exec(select(Usuario).where(Usuario.email == "nuevo@foodstore.com")).first()
>>>>>>> 703097aacb41fffe9f47a46130a99dbb10ef5027
    assert usuario_db is not None
    assert usuario_db.is_active is True

def test_login_usuario(client: TestClient):
<<<<<<< HEAD
    # First register
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "testlogin@foodstore.com",
            "password": "Password123",
            "nombre": "Test",
            "apellido": "Login"
        }
    )
    
    # Then login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testlogin@foodstore.com",
            "password": "Password123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.cookies
    
=======
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "cliente@foodstore.com",
            "password": "Cliente1234!"
        }
    )
    assert response.status_code == 200
    assert response.cookies.get("access_token") is not None

>>>>>>> 703097aacb41fffe9f47a46130a99dbb10ef5027
def test_login_invalid_credentials(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={
<<<<<<< HEAD
            "email": "notexists@foodstore.com",
            "password": "wrong"
        }
    )
    assert response.status_code == 401
=======
            "email": "cliente@foodstore.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_auth_me(client: TestClient, client_cookies: dict):
    response = client.get("/api/v1/auth/me", cookies=client_cookies)
    assert response.status_code == 200
    assert response.json()["email"] == "cliente@foodstore.com"
>>>>>>> 703097aacb41fffe9f47a46130a99dbb10ef5027
