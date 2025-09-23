from fastapi import APIRouter, Query
from typing import Optional
from app.services.ons_service import get_reservoir_data

router = APIRouter()

@router.get("/data/ear")
def get_ear_data(
    package_id: str = Query(..., description="Package ID do dataset EAR"),
    ano: Optional[int] = Query(None, description="Ano específico"),
    mes: Optional[int] = Query(None, description="Mês específico"),
    nome_reservatorio: Optional[str] = Query(None, description="Nome do reservatório para filtrar"),
    start_date: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    page: int = Query(1, description="Número da página"),
    page_size: int = Query(100, description="Tamanho da página")
):
    return get_reservoir_data(package_id, ano, mes, nome_reservatorio, start_date, end_date, page, page_size)

def get_ear_data_direct(
    package_id: str,
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    nome_reservatorio: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 100
):
    try:
        result = get_reservoir_data(
            package_id=package_id,
            ano=ano,
            mes=mes,
            nome_reservatorio=nome_reservatorio,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )
        
        if hasattr(result, 'body'):
            import json
            data = json.loads(result.body)
            return data.get('data', [])
        else:
            return result
    except Exception as e:
        print(f"Erro no ear_direct: {e}")
        return []