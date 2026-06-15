from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from datetime import date
from typing import List, Optional
from app.core.database import get_session
from app.modules.auth.dependencies import require_roles
from app.modules.estadisticas.service import EstadisticasService
from app.modules.estadisticas.repository import EstadisticasRepository
from app.modules.estadisticas.schemas import (
    ResumenResponse, VentasPeriodoItem, ProductoTopItem,
    PedidosEstadoItem, IngresosResponse
)

router = APIRouter(
    prefix="/estadisticas", 
    tags=["Estadísticas y Dashboard"],
    dependencies=[Depends(require_roles("ADMIN"))]
)

def get_estadisticas_service(session: Session = Depends(get_session)) -> EstadisticasService:
    repo = EstadisticasRepository(session)
    return EstadisticasService(repo)

@router.get("/resumen", response_model=ResumenResponse)
def get_resumen(svc: EstadisticasService = Depends(get_estadisticas_service)):
    return svc.get_resumen_kpis()

@router.get("/ventas", response_model=List[VentasPeriodoItem])
def get_ventas_periodo(
    desde: date,
    hasta: date,
    agrupacion: str = Query("day", description="day, week, month"),
    svc: EstadisticasService = Depends(get_estadisticas_service)
):
    return svc.get_ventas_periodo(desde, hasta, agrupacion)

@router.get("/productos-top", response_model=List[ProductoTopItem])
def get_productos_top(
    limit: int = 5,
    svc: EstadisticasService = Depends(get_estadisticas_service)
):
    return svc.get_productos_top(limit)

@router.get("/pedidos-por-estado", response_model=List[PedidosEstadoItem])
def get_pedidos_por_estado(svc: EstadisticasService = Depends(get_estadisticas_service)):
    return svc.get_pedidos_por_estado()

@router.get("/ingresos", response_model=IngresosResponse)
def get_ingresos_por_forma_pago(
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    svc: EstadisticasService = Depends(get_estadisticas_service)
):
    return svc.get_ingresos_por_forma_pago(desde, hasta)
