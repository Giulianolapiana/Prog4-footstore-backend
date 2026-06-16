import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from app.core.database import get_session
from app.core.security import hash_password
from app.modules.auth.models import Rol, Usuario, UsuarioRol
from app.modules.pedidos.models import EstadoPedido, FormaPago
from main import app

# Setup in-memory database for testing
sqlite_url = "sqlite:///:memory:"
engine = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

def override_get_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Mini-seed for tests
        roles = [
            Rol(codigo="ADMIN", nombre="Administrador"),
            Rol(codigo="STOCK", nombre="Gestor de Stock"),
            Rol(codigo="PEDIDOS", nombre="Gestor de Pedidos"),
            Rol(codigo="CLIENT", nombre="Cliente"),
        ]
        session.add_all(roles)
        
        estados = [
            EstadoPedido(codigo="PENDIENTE", nombre="Pendiente"),
            EstadoPedido(codigo="CONFIRMADO", nombre="Confirmado"),
            EstadoPedido(codigo="EN_PREP", nombre="En Preparación"),
            EstadoPedido(codigo="EN_CAMINO", nombre="En Camino"),
            EstadoPedido(codigo="ENTREGADO", nombre="Entregado"),
            EstadoPedido(codigo="CANCELADO", nombre="Cancelado"),
        ]
        session.add_all(estados)

        formas = [
            FormaPago(codigo="CASH", nombre="Efectivo"),
            FormaPago(codigo="MP", nombre="MercadoPago"),
        ]
        session.add_all(formas)
        session.commit()
        
        yield session
    
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    with TestClient(app) as client:
        yield client
