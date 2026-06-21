from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from app.modules.categorias.schemas import CategoriaResponse
from app.modules.ingredientes.schemas import IngredienteResponse

class IngredienteLink(BaseModel):
    ingrediente_id: int
    es_removible: bool = True
    es_opcional: bool = False
    cantidad: Decimal = Field(..., gt=0)
    unidad_medida_id: int = Field(...)

class UnidadMedidaResponse(BaseModel):
    id: int
    nombre: str
    simbolo: str
    tipo: str
    model_config = ConfigDict(from_attributes=True)

class ProductoIngredienteResponse(BaseModel):
    es_removible: bool
    es_opcional: bool
    cantidad: Decimal
    unidad_medida: Optional[UnidadMedidaResponse] = None
    ingrediente: IngredienteResponse
    model_config = ConfigDict(from_attributes=True)

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio_base: Decimal = Field(..., gt=0, decimal_places=2)
    stock_cantidad: Optional[int] = Field(default=None, ge=0)
    unidad_venta_id: int = Field(...)
    imagenes_url: Optional[List[str]] = []
    disponible: bool = True

# Esquema para creación de producto, requiere categorías e ingredientes
class ProductoCreate(ProductoBase):
    categoria_ids: List[int] = Field(..., min_length=1)
    ingredientes: List[IngredienteLink] = []

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=150)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio_base: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)
    stock_cantidad: Optional[int] = Field(default=None, ge=0)
    unidad_venta_id: Optional[int] = Field(default=None)
    imagenes_url: Optional[List[str]] = None
    disponible: Optional[bool] = None
    categoria_ids: Optional[List[int]] = Field(default=None, min_length=1)
    ingredientes: Optional[List[IngredienteLink]] = None

# NUEVO ESQUEMA PARA ACTUALIZAR SOLO DISPONIBILIDAD DEL PRODUCTO
class ProductoDisponibilidadUpdate(BaseModel):
    disponible: bool

class ProductoResponse(ProductoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    categorias: List[CategoriaResponse] = []
    producto_ingredientes: List[ProductoIngredienteResponse] = []
    unidad_venta: Optional[UnidadMedidaResponse] = None
    stock_cantidad: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)