from fastapi import APIRouter, Query
from app.services.registry_service import get_registry_data

router = APIRouter()

@router.get("/data/registry")
def get_registry(
    package_id: str = Query(..., description="Package ID for the registry dataset")
):
    return get_registry_data(package_id)