from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.uploads.repository import ImageRepository

class ImageUnitOfWork(UnitOfWork):
    def __init__(self, session: Session):
        super().__init__(session)
        self.images = ImageRepository(session)