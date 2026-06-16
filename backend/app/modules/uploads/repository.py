from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.uploads.models import ImageEntity

class ImageRepository(BaseRepository[ImageEntity]):
    
    def __init__(self, session: Session) -> None:
        super().__init__(session, ImageEntity)
    
    def get_all_ordered(self) -> list[ImageEntity]:
        """Devuelve las imágenes ordenadas de la más nueva a la más vieja"""
        statement = select(ImageEntity).order_by(ImageEntity.created_at.desc())
        return self.session.exec(statement).all()