from typing import Generic, TypeVar, Type, Sequence
from datetime import datetime, timezone
from sqlmodel import Session, SQLModel, select

ModelT = TypeVar("ModelT", bound=SQLModel)

class BaseRepository(Generic[ModelT]):
    def __init__(self, session: Session, model: Type[ModelT]) -> None:
        self.session = session
        self.model = model

    def get_by_id(self, record_id: int) -> ModelT | None:
        record = self.session.get(self.model, record_id)
        # Ignorar si está soft-deleted
        if record and getattr(record, "deleted_at", None) is not None:
            return None
        return record

    def get_all(self, offset: int = 0, limit: int = 100) -> Sequence[ModelT]:
        query = select(self.model)
        # Filtrar registros soft-deleted si el modelo tiene el campo
        if hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at == None)
            
        return self.session.exec(query.offset(offset).limit(limit)).all()

    def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)
        return instance

    def update(self, instance: ModelT) -> ModelT:
        if hasattr(instance, "updated_at"):
            instance.updated_at = datetime.now(timezone.utc)
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        """Aplica Soft Delete en lugar de borrar físicamente de la DB"""
        if hasattr(instance, "deleted_at"):
            instance.deleted_at = datetime.now(timezone.utc)
            self.session.add(instance)
        else:
            self.session.delete(instance)
        self.session.flush()