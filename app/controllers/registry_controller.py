from fastapi import APIRouter, Query
from app.services.registry_service import get_registry_data
from app.services.ons_service import fetch_package_metadata, find_parquet_url, read_parquet_from_url, records_from_dataframe

router = APIRouter()

@router.get("/data/registry")
def get_registry(
    package_id: str = Query(..., description="Package ID for the registry dataset")
):
    return get_registry_data(package_id)

def get_registry_direct(package_id: str):
    try:
        metadata = fetch_package_metadata(package_id)
        url = find_parquet_url(metadata)
        if not url:
            print("Nenhum arquivo parquet encontrado")
            return []
        
        df = read_parquet_from_url(url)
        records = records_from_dataframe(df)
        return records
        
    except Exception as e:
        print(f"Erro no registry_direct: {e}")
        return []
