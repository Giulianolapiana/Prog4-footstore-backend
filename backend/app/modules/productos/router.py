from decimal import Decimal
from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, Query, Path, status
from sqlmodel import Session

from app.core.database import get_session
# Importamos la protección de rutas
from app.core.security import AuthenticatedUser
from app.modules.auth.dependencies import require_roles
from app.modules.productos.schemas import (
    ProductoCreate, ProductoUpdate, ProductoResponse, ProductoDisponibilidadUpdate
)
from app.modules.productos.service import ProductoService

# El router de productos es público para GET, pero requiere autenticación y rol para POST, PUT, PATCH y DELETE
#implementamos el require_roles de nuestro módulo de seguridad para proteger las rutas de creación, actualización, cambio de disponibilidad y 
# eliminación de productos. Solo los usuarios con rol "ADMIN" podrán crear, actualizar o eliminar productos, mientras que tanto "ADMIN" como 
# "STOCK" podrán cambiar la disponibilidad de un producto. Las rutas GET seguirán siendo públicas para que los clientes puedan ver el catálogo sin necesidad de autenticarse.
router = APIRouter(prefix="/productos", tags=["Productos"])

SessionDep = Annotated[Session, Depends(get_session)]
SkipDep    = Annotated[int, Query(ge=0)]
LimitDep   = Annotated[int, Query(ge=1, le=100)]

def get_producto_service(session: SessionDep) -> ProductoService:
    return ProductoService(session)

from app.core.pagination import PaginatedResponse

# PÚBLICO: Los clientes necesitan ver el catálogo
@router.get("/", response_model=PaginatedResponse[ProductoResponse])
def get_productos(
    skip: SkipDep = 0,
    limit: LimitDep = 20,
    nombre: Optional[str] = None,
    disponible: Optional[bool] = None,
    precio_min: Optional[Decimal] = None,
    precio_max: Optional[Decimal] = None,
    svc: ProductoService = Depends(get_producto_service),
):
    return svc.get_all(skip, limit, nombre, disponible, precio_min, precio_max)

# PÚBLICO
@router.get("/{producto_id}", response_model=ProductoResponse)
def get_producto(
    producto_id: Annotated[int, Path(ge=1)],
    svc: ProductoService = Depends(get_producto_service),
):
    return svc.get_by_id(producto_id)

# PRIVADO: Solo ADMIN
@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def create_producto(
    data: ProductoCreate,
    svc: ProductoService = Depends(get_producto_service),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN"))
):
    return svc.create(data)

# PRIVADO: Solo ADMIN
@router.put("/{producto_id}", response_model=ProductoResponse)
def update_producto(
    producto_id: Annotated[int, Path(ge=1)],
    data: ProductoUpdate,
    svc: ProductoService = Depends(get_producto_service),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN"))
):
    return svc.update(producto_id, data)

# PRIVADO: ADMIN y STOCK (Requisito del Parcial)
@router.patch("/{producto_id}/disponibilidad", response_model=ProductoResponse)
def update_disponibilidad(
    producto_id: Annotated[int, Path(ge=1)],
    data: ProductoDisponibilidadUpdate,
    svc: ProductoService = Depends(get_producto_service),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN", "STOCK"))
):
    return svc.patch_disponibilidad(producto_id, data.disponible)

# PRIVADO: Solo ADMIN
@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(
    producto_id: Annotated[int, Path(ge=1)],
    svc: ProductoService = Depends(get_producto_service),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN"))
):
    svc.delete(producto_id)
