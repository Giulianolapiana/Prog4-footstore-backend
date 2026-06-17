import pytest
from fastapi.testclient import TestClient

def test_websocket_connection_and_auth(client: TestClient):
    response = client.post("/api/v1/auth/login", json={"email": "admin@foodstore.com", "password": "Admin1234!"})
    token = response.json().get("access_token")
    
    with client.websocket_connect(f"/ws/pedidos?token={token}") as websocket:
        pass

def test_websocket_invalid_auth(client: TestClient):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/pedidos"):
            pass
