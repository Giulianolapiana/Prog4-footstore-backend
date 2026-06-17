import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.modules.auth.models import Usuario

def test_register_usuario(client: TestClient, db_session: Session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nuevo@foodstore.com",
            "password": "Password123!",
            "nombre": "Nuevo",
            "apellido": "User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "nuevo@foodstore.com"
    
    usuario_db = db_session.exec(select(Usuario).where(Usuario.email == "nuevo@foodstore.com")).first()
    assert usuario_db is not None
    assert usuario_db.is_active is True

def test_login_usuario(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "cliente@foodstore.com",
            "password": "Cliente1234!"
        }
    )
    assert response.status_code == 200
    assert response.cookies.get("access_token") is not None

def test_login_invalid_credentials(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "cliente@foodstore.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_auth_me(client: TestClient, client_cookies: dict):
    response = client.get("/api/v1/auth/me", cookies=client_cookies)
    assert response.status_code == 200
    assert response.json()["email"] == "cliente@foodstore.com"
