from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, Query, Path, status
from sqlmodel import Session
from app.core.database import get_session
from app.core.security import AuthenticatedUser
from app.modules.auth.dependencies import require_roles
from app.modules.categorias.schemas import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from app.modules.categorias.service import CategoriaService

router = APIRouter(prefix="/categorias", tags=["Categorías"])

SessionDep = Annotated[Session, Depends(get_session)]
SkipDep    = Annotated[int, Query(ge=0)]
LimitDep   = Annotated[int, Query(ge=1, le=100)]

def get_categoria_service(session: SessionDep) -> CategoriaService:
    return CategoriaService(session)

# Endpoint PÚBLICO
@router.get("/", response_model=List[CategoriaResponse])
def get_categorias(
    skip: SkipDep = 0,
    limit: LimitDep = 20,
    nombre: Annotated[Optional[str], Query(description="Filtrar por nombre")] = None,
    # REQUISITO EXPLICITO: Annotated y Query para filtro de parent_id
    parent_id: Annotated[Optional[int], Query(description="Filtrar por categoría padre")] = None,
    svc: CategoriaService = Depends(get_categoria_service),
):
    return svc.get_all(skip=skip, limit=limit, nombre=nombre, parent_id=parent_id)

# Endpoint PÚBLICO
@router.get("/{categoria_id}", response_model=CategoriaResponse)
def get_categoria(
    categoria_id: Annotated[int, Path(ge=1)],
    svc: CategoriaService = Depends(get_categoria_service),
):
    return svc.get_by_id(categoria_id)

# PRIVADO: Solo ADMIN
@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def create_categoria(
    data: CategoriaCreate,
    svc: CategoriaService = Depends(get_categoria_service),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN"))
):
    return svc.create(data)

# PRIVADO: Solo ADMIN
@router.put("/{categoria_id}", response_model=CategoriaResponse)
def update_categoria(
    categoria_id: Annotated[int, Path(ge=1)],
    data: CategoriaUpdate,
    svc: CategoriaService = Depends(get_categoria_service),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN"))
):
    return svc.update(categoria_id, data)

# PRIVADO: Solo ADMIN
@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(
    categoria_id: Annotated[int, Path(ge=1)],
    svc: CategoriaService = Depends(get_categoria_service),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN"))
):
    svc.delete(categoria_id)