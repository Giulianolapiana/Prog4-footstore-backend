from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ImagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    public_id: str
    url: str
    filename: str
    format: Optional[str]
    width: Optional[int]
    height: Optional[int]
    bytes: Optional[int]
    created_at: datetime