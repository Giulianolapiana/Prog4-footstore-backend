from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, Query, Path, status
from sqlmodel import Session
#importar require_roles de tu core.security y agregarlo solo a POST, PUT y DELETE. El GET queda público para el catálogo

from app.core.database import get_session
from app.core.security import AuthenticatedUser
from app.modules.auth.dependencies import require_roles
from app.modules.ingredientes.schemas import IngredienteCreate, IngredienteUpdate, IngredienteResponse
from app.modules.ingredientes.service import IngredienteService

router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])

SessionDep = Annotated[Session, Depends(get_session)]
SkipDep = Annotated[int, Query(ge=0)]
LimitDep = Annotated[int, Query(ge=1, le=100)]

def get_ingrediente_service(session: SessionDep) -> IngredienteService:
    return IngredienteService(session)

# GET: Público (El cliente necesita ver esto para el catálogo)
@router.get("/", response_model=List[IngredienteResponse])
def get_ingredientes(
    skip: SkipDep = 0,
    limit: LimitDep = 100,
    nombre: Optional[str] = None,
    solo_alergenos: Optional[bool] = None,
    svc: IngredienteService = Depends(get_ingrediente_service),
):
    return svc.get_all(skip, limit, nombre, solo_alergenos)

# GET ID: Público
@router.get("/{ingrediente_id}", response_model=IngredienteResponse)
def get_ingrediente(
    ingrediente_id: Annotated[int, Path(ge=1)],
    svc: IngredienteService = Depends(get_ingrediente_service),
):
    return svc.get_by_id(ingrediente_id)

# POST: Protegido (Solo ADMIN)
@router.post("/", response_model=IngredienteResponse, status_code=status.HTTP_201_CREATED)
def create_ingrediente(
    data: IngredienteCreate,
    svc: IngredienteService = Depends(get_ingrediente_service),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN"))
):
    return svc.create(data)

# PUT: Protegido (Solo ADMIN)
@router.put("/{ingrediente_id}", response_model=IngredienteResponse)
def update_ingrediente(
    ingrediente_id: Annotated[int, Path(ge=1)],
    data: IngredienteUpdate,
    svc: IngredienteService = Depends(get_ingrediente_service),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN"))
):
    return svc.update(ingrediente_id, data)

# DELETE: Protegido (Solo ADMIN)
@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingrediente(
    ingrediente_id: Annotated[int, Path(ge=1)],
    svc: IngredienteService = Depends(get_ingrediente_service),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN"))
):
    svc.delete(ingrediente_id)