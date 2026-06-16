import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.modules.auth.models import Usuario

def test_register_usuario(client: TestClient, session: Session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@foodstore.com",
            "password": "Password123",
            "nombre": "Test",
            "apellido": "User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@foodstore.com"
    assert data["nombre"] == "Test"
    
    # Check db
    usuario_db = session.exec(select(Usuario).where(Usuario.email == "test@foodstore.com")).first()
    assert usuario_db is not None
    assert usuario_db.is_active is True

def test_login_usuario(client: TestClient):
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
    
def test_login_invalid_credentials(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "notexists@foodstore.com",
            "password": "wrong"
        }
    )
    assert response.status_code == 401
