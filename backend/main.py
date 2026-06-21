from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import create_db_and_tables
from app.modules.seed.seed import run_seed
from app.core.cloudinary_setup import init_cloudinary
from app.modules.uploads.router import router as router_uploads

# Core Features
from app.core.logger import setup_logging
from app.core.exceptions.exception_handlers import register_exception_handlers
from app.core.middleware.logging_middleware import LoggingMiddleware
from app.core.middleware.timing_middleware import TimingMiddleware
from app.core.rate_limit.rate_limit_middleware import RateLimitMiddleware

# Routers modulares
from app.modules.categorias.router import router as router_categorias
from app.modules.ingredientes.router import router as router_ingredientes
from app.modules.productos.router import router as router_productos
from app.modules.auth.router import router as router_auth
from app.modules.direcciones.router import router as router_direcciones
from app.modules.pedidos.router import router as router_pedidos
from app.modules.admin.router import router as router_admin
from app.modules.estadisticas.router import router as router_estadisticas
from app.modules.pedidos.ws_router import router as router_ws_pedidos
from app.modules.pagos.router import router as router_pagos


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()  # Configurar logger al inicio
    create_db_and_tables()
    run_seed()
    init_cloudinary()
    yield


app = FastAPI(
    title="FoodStore — API",
    description=(
        "API REST fullstack para FoodStore con parte Admin y Cliente\n\n"
        "**Stack:** FastAPI + SQLModel + PostgreSQL\n\n"
        "**Parcial 2 — Programación IV · UTN**"
    ),
    version="6.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Exception Handlers
register_exception_handlers(app)

# Middlewares (se ejecutan en orden inverso al que se añaden, el último añadido es el más exterior)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(LoggingMiddleware)

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
app.include_router(router_estadisticas, prefix="/api/v1")
app.include_router(router_ws_pedidos)
app.include_router(router_uploads, prefix="/api/v1")
app.include_router(router_pagos, prefix="/api/v1")


# ── Endpoint de control ───────────────────────────────────────────────────────
@app.get("/", tags=["Root"], summary="Health check")
def read_root():
    return {
        "status": "ok", 
        "message": "API FoodStore funcionando correctamente. Visita /docs para ver Swagger."
    }
