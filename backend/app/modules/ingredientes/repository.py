from typing import List, Optional
from sqlmodel import Session, select, col
from app.core.repository import BaseRepository
from app.modules.ingredientes.models import Ingrediente


class IngredienteRepository(BaseRepository[Ingrediente]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Ingrediente)

    def get_active(
        self,
        skip: int = 0,
        limit: int = 100,
        nombre: Optional[str] = None,
        solo_alergenos: Optional[bool] = None,
    ) -> List[Ingrediente]:
        query = select(Ingrediente).where(Ingrediente.deleted_at.is_(None))
        if nombre:
            query = query.where(col(Ingrediente.nombre).icontains(nombre))
        if solo_alergenos is not None:
            query = query.where(Ingrediente.es_alergeno == solo_alergenos)
        return self.session.exec(query.offset(skip).limit(limit)).all()

    def get_by_nombre(self, nombre: str) -> Ingrediente | None:
        return self.session.exec(
            select(Ingrediente).where(Ingrediente.nombre == nombre)
        ).first()
