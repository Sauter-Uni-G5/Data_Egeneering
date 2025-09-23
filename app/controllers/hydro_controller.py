from fastapi import APIRouter, Query
from typing import Optional
from app.services.ons_service import get_reservoir_data

router = APIRouter()

@router.get("/data/hydro")
def get_hydro_data(
    package_id: str = Query(..., description="Package ID do dataset hidráulico"),
    ano: Optional[int] = Query(None, description="Ano específico"),
    mes: Optional[int] = Query(None, description="Mês específico"),
    nome_reservatorio: Optional[str] = Query(None, description="Nome do reservatório para filtrar"),
    start_date: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    page: int = Query(1, description="Número da página"),
    page_size: int = Query(100, description="Tamanho da página")
):
    return get_reservoir_data(package_id, ano, mes, nome_reservatorio, start_date, end_date, page, page_size)