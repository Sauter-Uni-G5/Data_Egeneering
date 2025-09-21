from app.services.ons_service import fetch_package_metadata, find_parquet_url, read_parquet_from_url, records_from_dataframe
from fastapi.responses import JSONResponse

def get_registry_data(package_id: str):
    try:
        metadata = fetch_package_metadata(package_id)
        url = find_parquet_url(metadata)
        if not url:
            return JSONResponse({"error": "No parquet file found for this package_id."}, status_code=404)
        df = read_parquet_from_url(url)
        records = records_from_dataframe(df)
        return JSONResponse({"data": records})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)