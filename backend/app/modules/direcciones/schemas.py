from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DireccionBase(BaseModel):
    calle: str
    numero: str
    piso: Optional[str] = None
    depto: Optional[str] = None
    ciudad: str
    codigo_postal: Optional[str] = None
    alias: str
    es_principal: bool = False

class DireccionCreate(DireccionBase):
    pass

class DireccionResponse(DireccionBase):
    id: int
    usuario_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)