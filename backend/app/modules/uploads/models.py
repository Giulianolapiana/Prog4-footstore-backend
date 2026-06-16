from typing import Optional
from sqlmodel import Field
from app.core.base_model import BaseEntity

class ImageEntity(BaseEntity, table=True):
    __tablename__ = "imagenes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    public_id: str = Field(index=True, unique=True, description="ID único en Cloudinary")
    url: str = Field(description="URL segura para mostrar en el frontend")
    filename: str = Field(description="Nombre original del archivo subido")
    format: Optional[str] = Field(default=None)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    bytes: Optional[int] = Field(default=None)