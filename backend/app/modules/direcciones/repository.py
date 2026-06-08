from sqlmodel import Session, select
from typing import Sequence
from app.core.repository import BaseRepository
from app.modules.direcciones.models import DireccionEntrega

class DireccionRepository(BaseRepository[DireccionEntrega]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DireccionEntrega)

    def get_by_usuario(self, usuario_id: int) -> Sequence[DireccionEntrega]:
        query = select(DireccionEntrega).where(
            DireccionEntrega.usuario_id == usuario_id,
            DireccionEntrega.deleted_at == None
        )
        return self.session.exec(query).all()

    def desmarcar_principales(self, usuario_id: int) -> None:
        """Pasa todas las direcciones del usuario a es_principal = False"""
        direcciones = self.get_by_usuario(usuario_id)
        for d in direcciones:
            if d.es_principal:
                d.es_principal = False
                self.session.add(d)
        self.session.flush()