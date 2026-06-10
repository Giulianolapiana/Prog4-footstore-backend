from sqlmodel import select
from app.core.repository import BaseRepository
from app.modules.images.models import ImageEntity

class ImageRepository(BaseRepository[ImageEntity]):
    
    def get_all_ordered(self) -> list[ImageEntity]:
        """Devuelve las imágenes ordenadas de la más nueva a la más vieja"""
        statement = select(ImageEntity).order_by(ImageEntity.created_at.desc())
        return self.session.exec(statement).all()