from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.auth.repository import UsuarioRepository, RolRepository

class AuthUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.usuarios = UsuarioRepository(session)
        self.roles = RolRepository(session)