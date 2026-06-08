from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import create_db_and_tables
from app.modules.seed.seed import run_seed

# Routers modulares
from app.modules.categorias.router import router as router_categorias
from app.modules.ingredientes.router import router as router_ingredientes
from app.modules.productos.router import router as router_productos
from app.modules.auth.router import router as router_auth
from app.modules.direcciones.router import router as router_direcciones
from app.modules.pedidos.router import router as router_pedidos
from app.modules.admin.router import router as router_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Al arrancar, verificamos/creamos las tablas en PostgreSQL
    create_db_and_tables()
    # 2. Corremos el seed para inyectar roles, estados y el admin por defecto
    run_seed()
    yield


app = FastAPI(
    title="FoodStore — API",
    description=(
        "API REST fullstack para FoodStore con parte Admin y Cliente\n\n"
        "**Stack:** FastAPI + SQLModel + PostgreSQL\n\n"
        "**Parcial 2 — Programación IV · UTN**"
    ),
    version="5.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Admin Vite
        "http://localhost:5174",  # Store Vite
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers 

app.include_router(router_auth, prefix="/api/v1")
app.include_router(router_categorias, prefix="/api/v1")
app.include_router(router_ingredientes, prefix="/api/v1")
app.include_router(router_productos, prefix="/api/v1")
app.include_router(router_direcciones, prefix="/api/v1")
app.include_router(router_pedidos, prefix="/api/v1")
app.include_router(router_admin, prefix="/api/v1")

#  Manejador de errores de validación de Pydantic 
# Traduce los mensajes automáticos de FastAPI al español
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        err_type = error.get("type")
        message = error.get("msg")

        # Mapeo de errores comunes → español
        if err_type == "missing":
            message = "Este campo es obligatorio"
        elif err_type == "string_too_long":
            ctx = error.get("ctx", {})
            limit = ctx.get("max_length") or ctx.get("limit_value") or 150
            message = f"El texto es demasiado largo (máximo {limit} caracteres)"
        elif err_type == "string_too_short":
            ctx = error.get("ctx", {})
            limit = ctx.get("min_length") or ctx.get("limit_value") or 2
            message = f"El texto es demasiado corto (mínimo {limit} caracteres)"
        elif "greater_than" in (err_type or ""):
            limit = error.get("ctx", {}).get("limit_value") or error.get("ctx", {}).get("gt")
            message = f"El valor debe ser mayor a {limit}"
        elif "less_than" in (err_type or ""):
            limit = error.get("ctx", {}).get("limit_value") or error.get("ctx", {}).get("lt")
            message = f"El valor debe ser menor a {limit}"

        errors.append({
            "loc": error.get("loc"),
            "msg": message,
            "type": err_type,
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors},
    )

# ── Endpoint de control ───────────────────────────────────────────────────────
@app.get("/", tags=["Root"], summary="Health check")
def read_root():
    return {
        "status": "ok", 
        "message": "API FoodStore funcionando correctamente. Visita /docs para ver Swagger."
    }
