from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class BaseEntity(SQLModel):
    """Base para todas las entidades de negocio con auditoría básica."""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: datetime | None = Field(default=None)