from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.auth.models import Usuario, Rol

#core.repository ya trae las funciones
class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Usuario)

    def get_by_email(self, email: str) -> Usuario | None:
        return self.session.exec(
            select(Usuario).where(Usuario.email == email)
        ).first()

    def get_all_with_filters(self, skip: int = 0, limit: int = 50, rol_codigo: str | None = None) -> list[Usuario]:
        query = select(Usuario).where(Usuario.deleted_at == None)
        if rol_codigo:
            query = query.join(Usuario.roles).where(Rol.codigo == rol_codigo)
        return self.session.exec(query.offset(skip).limit(limit)).all()

class RolRepository(BaseRepository[Rol]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Rol)

    def get_by_codigo(self, codigo: str) -> Rol | None:
        return self.session.exec(
            select(Rol).where(Rol.codigo == codigo)
        ).first()