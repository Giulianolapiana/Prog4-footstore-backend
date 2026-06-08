from sqlmodel import create_engine, SQLModel, Session
from .config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    """Crea todas las tablas en la base de datos si no existen."""
    # Importar explícitamente los módulos de modelos para asegurar que
    # todas las clases estén registradas en el mapper antes de crear
    # las tablas o ejecutar consultas (evita problemas de orden de import).
    try:
        # Importar módulos que definen modelos (registro de mappers)
        import app.modules.productos.models  # noqa: F401
        import app.modules.categorias.models  # noqa: F401
        import app.modules.ingredientes.models  # noqa: F401
        import app.modules.usuarios.models  # noqa: F401
    except Exception:
        # Ignorar errores de importación aquí: si fallan, create_all puede
        # igualmente intentarlo y los errores se verán más arriba.
        pass

    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency de FastAPI: provee una sesión de DB por request."""
    with Session(engine) as session:
        yield session
