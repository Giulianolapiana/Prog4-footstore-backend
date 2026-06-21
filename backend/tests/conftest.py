<<<<<<< HEAD
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
=======
import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import get_session
from app.core.security import hash_password
from main import app
from app.modules.auth.models import Rol, Usuario, UsuarioRol
from app.modules.pedidos.models import EstadoPedido, FormaPago
from app.modules.productos.models import Producto, UnidadMedida
from app.modules.categorias.models import Categoria
from app.modules.direcciones.models import DireccionEntrega
from app.core.rate_limit.rate_limit_middleware import RateLimitMiddleware

os.environ.setdefault("ENVIRONMENT", "test")
# Aumentamos los límites durante los tests para que no bloqueen los flujos
settings.rate_limit_auth_burst = 9999
settings.rate_limit_default_burst = 9999

# ===========================================================================
# 1. ENGINE DE TEST
# ===========================================================================
@pytest.fixture(name="engine_test", scope="session")
def engine_test_fixture():
    sqlite_url = "sqlite:///:memory:"
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    yield engine
    engine.dispose()

# ===========================================================================
# 2. SESSION DE BASE DE DATOS
# ===========================================================================
@pytest.fixture(name="db_session", scope="function")
def session_fixture(engine_test):
    SQLModel.metadata.create_all(engine_test)
    try:
        with Session(engine_test) as session:
            _seed_test_db(session)
            yield session
    finally:
        SQLModel.metadata.drop_all(engine_test)

def _seed_test_db(session: Session):
    roles = [
        Rol(codigo="ADMIN", nombre="Administrador"),
        Rol(codigo="STOCK", nombre="Gestor de Stock"),
        Rol(codigo="PEDIDOS", nombre="Gestor de Pedidos"),
        Rol(codigo="CLIENT", nombre="Cliente"),
    ]
    session.add_all(roles)

    # FSM v7 (Sin EN_CAMINO)
    estados = [
        EstadoPedido(codigo="PENDIENTE", nombre="Pendiente"),
        EstadoPedido(codigo="CONFIRMADO", nombre="Confirmado"),
        EstadoPedido(codigo="EN_PREP", nombre="En Preparación"),
        EstadoPedido(codigo="ENTREGADO", nombre="Entregado"),
        EstadoPedido(codigo="CANCELADO", nombre="Cancelado"),
    ]
    session.add_all(estados)

    unidades = [
        UnidadMedida(nombre="Kilogramo", simbolo="kg", tipo="peso"),
        UnidadMedida(nombre="Unidad", simbolo="ud", tipo="contable"),
    ]
    session.add_all(unidades)

    categorias = [
        Categoria(nombre="Hamburguesas", descripcion="Ricas"),
    ]
    session.add_all(categorias)

    formas = [
        FormaPago(codigo="EFECTIVO", nombre="Efectivo"),
        FormaPago(codigo="MERCADOPAGO", nombre="MercadoPago"),
        FormaPago(codigo="TRANSFERENCIA", nombre="Transferencia"),
    ]
    session.add_all(formas)

    admin = Usuario(
        email="admin@foodstore.com",
        hashed_password=hash_password("Admin1234!"),
        nombre="Admin",
        apellido="Test",
        is_active=True
    )
    cliente = Usuario(
        email="cliente@foodstore.com",
        hashed_password=hash_password("Cliente1234!"),
        nombre="Cliente",
        apellido="Test",
        is_active=True
    )
    pedidos_user = Usuario(
        email="pedidos@foodstore.com",
        hashed_password=hash_password("Pedidos1234!"),
        nombre="Pedidos",
        apellido="Test",
        is_active=True
    )
    session.add_all([admin, cliente, pedidos_user])
    session.commit()

    rol_admin = session.exec(select(Rol).where(Rol.codigo == "ADMIN")).first()
    rol_client = session.exec(select(Rol).where(Rol.codigo == "CLIENT")).first()
    rol_pedidos = session.exec(select(Rol).where(Rol.codigo == "PEDIDOS")).first()

    session.add(UsuarioRol(usuario_id=admin.id, rol_id=rol_admin.id))
    session.add(UsuarioRol(usuario_id=cliente.id, rol_id=rol_client.id))
    session.add(UsuarioRol(usuario_id=pedidos_user.id, rol_id=rol_pedidos.id))

    # Add a mock Direccion for the client
    direccion = DireccionEntrega(
        usuario_id=cliente.id,
        calle="Calle Falsa",
        numero="123",
        codigo_postal="1234",
        ciudad="Springfield",
        alias="Casa"
    )
    session.add(direccion)
    session.commit()


# ===========================================================================
# 3. CLIENTE HTTP DE TEST
# ===========================================================================
@pytest.fixture(name="client", scope="function")
def client_fixture(db_session: Session):
    def get_session_override():
        return db_session

    app.dependency_overrides[get_session] = get_session_override
    RateLimitMiddleware.reset_all_limiters()

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

# ===========================================================================
# 4. HEADERS DE AUTENTICACIÓN
# ===========================================================================
def _login_and_get_cookies(client: TestClient, email: str, password: str) -> dict:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, f"Login failed for {email}: {response.text}"
    token = response.cookies.get("access_token")
    return {"access_token": token}

@pytest.fixture(name="admin_cookies")
def admin_cookies_fixture(client: TestClient) -> dict:
    return _login_and_get_cookies(client, "admin@foodstore.com", "Admin1234!")

@pytest.fixture(name="client_cookies")
def client_cookies_fixture(client: TestClient) -> dict:
    return _login_and_get_cookies(client, "cliente@foodstore.com", "Cliente1234!")

@pytest.fixture(name="pedidos_cookies")
def pedidos_cookies_fixture(client: TestClient) -> dict:
    return _login_and_get_cookies(client, "pedidos@foodstore.com", "Pedidos1234!")

# ===========================================================================
# 5. FACTORIES
# ===========================================================================
@pytest.fixture(name="producto_factory")
def producto_factory_fixture(db_session: Session):
    def _create_producto(nombre="Burger Test", precio=1000.0, stock=50):
        unidad = db_session.exec(select(UnidadMedida).where(UnidadMedida.simbolo == "ud")).first()
        categoria = db_session.exec(select(Categoria)).first()
        prod = Producto(
            nombre=nombre,
            descripcion="Descripción test",
            precio_base=precio,
            stock_cantidad=stock,
            disponible=True,
            imagenes_url=["http://cloudinary.com/test.jpg"],
            unidad_venta_id=unidad.id
        )
        db_session.add(prod)
        db_session.commit()
        db_session.refresh(prod)
        
        from app.modules.productos.models import ProductoCategoria
        link = ProductoCategoria(producto_id=prod.id, categoria_id=categoria.id, es_principal=True)
        db_session.add(link)
        db_session.commit()

        return prod
    return _create_producto

@pytest.fixture(name="pedido_factory")
def pedido_factory_fixture(client: TestClient, client_cookies: dict, db_session: Session, producto_factory):
    def _create_pedido():
        prod = producto_factory()
        # Find forma_pago EFECTIVO
        forma = db_session.exec(select(FormaPago).where(FormaPago.codigo == "EFECTIVO")).first()
        # Find client's address
        direccion = db_session.exec(select(DireccionEntrega)).first()
        payload = {
            "forma_pago_id": forma.id,
            "direccion_entrega_id": direccion.id,
            "detalles": [
                {"producto_id": prod.id, "cantidad": 2}
            ]
        }
        res = client.post("/api/v1/pedidos/", json=payload, cookies=client_cookies)
        assert res.status_code == 201
        return res.json()
    return _create_pedido
>>>>>>> 703097aacb41fffe9f47a46130a99dbb10ef5027
