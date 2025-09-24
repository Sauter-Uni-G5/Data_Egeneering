from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import tempfile
import os
import pandas as pd
from app.controllers.registry_controller import get_registry_direct
from app.controllers.ear_controller import get_ear_data_direct
from app.controllers.hydro_controller import get_hydro_data_direct
from app.pipeline.extractors.ons_extractor import (
    extract_registry_to_df, extract_ear_to_df, extract_hydro_to_df
)
from app.pipeline.transformers.data_cleaner import clean_and_normalize
from app.pipeline.transformers.aggregator import aggregate_ear_hydro_registry
from app.services.gcs_service import upload_to_gcs
from app.pipeline.extractors.weather_parallel import fetch_weather_batch

router = APIRouter()

@router.post("/data/full-pipeline")
def run_full_pipeline(
    registry_package_id: str = Query(..., description="Package ID do metadados dos reservatórios"),
    ear_package_id: str = Query(..., description="Package ID do EAR"),
    hydro_package_id: str = Query(..., description="Package ID do Hydro"),
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
):
    try:
        # 1. Extrai e limpa Registry
        raw_registry = get_registry_direct(registry_package_id)
        df_registry = extract_registry_to_df(raw_registry)
        df_registry_clean = clean_and_normalize(df_registry)

        # 2. Extrai e limpa EAR
        raw_ear = get_ear_data_direct(ear_package_id, start_date=start_date, end_date=end_date, page_size=10000)
        df_ear = extract_ear_to_df(raw_ear)
        df_ear_clean = clean_and_normalize(df_ear, date_col="ear_data" if "ear_data" in df_ear.columns else None)

        # 3. Extrai e limpa Hydro
        raw_hydro = get_hydro_data_direct(hydro_package_id, start_date=start_date, end_date=end_date, page_size=10000)
        df_hydro = extract_hydro_to_df(raw_hydro)
        df_hydro_clean = clean_and_normalize(df_hydro, date_col="din_instante" if "din_instante" in df_hydro.columns else None)

        # 4. Agregação final
        df_final = aggregate_ear_hydro_registry(df_ear_clean, df_hydro_clean, df_registry_clean)
        
        df_weather = fetch_weather_batch(df_final, start_date=start_date, end_date=end_date, max_workers=5)

        df_final = pd.merge(
            df_final,
            df_weather,
            on=["id_reservatorio", "ear_data"],
            how="left"
        )

        df_final = df_final.drop(columns=["nom_bacia", "ear_data", "tip_reservatorio", "nom_reservatorio"])

        # 5. Salva CSV temporário
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_csv:
            df_final.to_csv(temp_csv.name, index=False, encoding="utf-8", sep=";")
            temp_csv_path = temp_csv.name

        # 6. Envia para GCS
        bucket_name = "sauter_university"
        gcs_blob_name = f"Data_Engineering/processed/pipeline_{start_date}_{end_date}.csv"
        gcs_url = upload_to_gcs(bucket_name, temp_csv_path, gcs_blob_name)

        # 7. Remove arquivo temporário
        os.remove(temp_csv_path)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Pipeline executada com sucesso",
                "gcs_url": gcs_url,
                "rows": len(df_final)
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )