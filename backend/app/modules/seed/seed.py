from sqlmodel import Session, select
from app.core.database import engine
from app.core.security import hash_password
from app.modules.auth.models import Rol, Usuario, UsuarioRol
# Importá tus modelos de pedidos (asegurate de tenerlos creados con estos nombres o ajustalos luego)
from app.modules.pedidos.models import EstadoPedido, FormaPago

def run_seed():
    """Ejecuta la carga de datos iniciales en la base de datos."""
    with Session(engine) as session:
        # 1. Chequear si la base ya tiene datos (para no duplicar si corremos el script dos veces)
        if session.exec(select(Rol)).first():
            print("Los datos iniciales (Seed) ya están cargados. Saltando...")
            return

        print("Iniciando carga de datos Seed...")

        # 2. Cargar Roles Obligatorios
        roles = [
            Rol(codigo="ADMIN", nombre="Administrador"),
            Rol(codigo="STOCK", nombre="Gestor de Stock"),
            Rol(codigo="PEDIDOS", nombre="Gestor de Pedidos"),
            Rol(codigo="CLIENT", nombre="Cliente"),
        ]
        session.add_all(roles)
        session.flush() # Flush para que la BD les asigne IDs, nvías los datos a la base de datos temporalmente

        # 3. Cargar Estados de Pedido
        if not session.exec(select(EstadoPedido)).first():
            estados = [
                EstadoPedido(codigo="PENDIENTE", nombre="Pendiente"),
                EstadoPedido(codigo="CONFIRMADO", nombre="Confirmado"),
                EstadoPedido(codigo="EN_PREP", nombre="En Preparación"),
                EstadoPedido(codigo="EN_CAMINO", nombre="En Camino"),
                EstadoPedido(codigo="ENTREGADO", nombre="Entregado"),
                EstadoPedido(codigo="CANCELADO", nombre="Cancelado"),
            ]
            session.add_all(estados)

        # 4. Cargar Formas de Pago
        if not session.exec(select(FormaPago)).first():
            formas = [
                FormaPago(codigo="CASH", nombre="Efectivo"),
                FormaPago(codigo="DEBIT", nombre="Tarjeta de Débito"),
                FormaPago(codigo="CREDIT", nombre="Tarjeta de Crédito"),
                FormaPago(codigo="MP", nombre="MercadoPago"),
            ]
            session.add_all(formas)

        # 5. Crear Usuario Admin por defecto
        admin_user = Usuario(
            email="admin@foodstore.com",
            hashed_password=hash_password("admin123"), # Contraseña por defecto
            nombre="Admin",
            apellido="FoodStore",
            is_active=True
        )
        session.add(admin_user)
        session.flush()

        # 6. Asignar el rol ADMIN al usuario creado
        rol_admin_db = session.exec(select(Rol).where(Rol.codigo == "ADMIN")).first()
        if rol_admin_db:
            relacion_rol = UsuarioRol(usuario_id=admin_user.id, rol_id=rol_admin_db.id)
            session.add(relacion_rol)

        # 7. Finalmente, hacemos commit de toda la transacción
        session.commit()
        print("Seed data cargada exitosamente.")

if __name__ == "__main__":
    run_seed()