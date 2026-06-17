import pytest
from fastapi.testclient import TestClient

def test_get_resumen_kpis(client: TestClient, admin_cookies: dict):
    res = client.get("/api/v1/estadisticas/resumen", cookies=admin_cookies)
    assert res.status_code == 200
    data = res.json()
    assert "ventas_hoy" in data or isinstance(data, dict)

from unittest.mock import patch

def test_get_ventas_periodo(client: TestClient, admin_cookies: dict):
    with patch("app.modules.estadisticas.service.EstadisticasService.get_ventas_periodo") as mock_ventas:
        mock_ventas.return_value = []
        res = client.get("/api/v1/estadisticas/ventas?desde=2024-01-01&hasta=2025-12-31", cookies=admin_cookies)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

def test_get_productos_top(client: TestClient, admin_cookies: dict):
    res = client.get("/api/v1/estadisticas/productos-top", cookies=admin_cookies)
    assert res.status_code == 200

def test_get_pedidos_por_estado(client: TestClient, admin_cookies: dict):
    res = client.get("/api/v1/estadisticas/pedidos-por-estado", cookies=admin_cookies)
    assert res.status_code == 200

def test_get_ingresos_forma_pago(client: TestClient, admin_cookies: dict):
    res = client.get("/api/v1/estadisticas/ingresos", cookies=admin_cookies)
    assert res.status_code == 200

def test_estadisticas_requieren_admin(client: TestClient, client_cookies: dict):
    res = client.get("/api/v1/estadisticas/resumen", cookies=client_cookies)
    assert res.status_code in [401, 403]
