from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from datetime import datetime
import tempfile
import os
import pandas as pd
import logging
import traceback  # ADICIONAR

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
from app.services.bigquery_service import BigQueryService

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/pipeline/run")
async def run_pipeline(
    registry_package_id: str = Query(..., description="Package ID do metadados dos reservatórios"),
    ear_package_id: str = Query(..., description="Package ID do EAR"),
    hydro_package_id: str = Query(..., description="Package ID do Hydro"),
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)"),
    load_to_bigquery: bool = Query(True, description="Carregar dados no BigQuery")
):
    try:
        logger.info("Iniciando pipeline...")
        
        raw_registry = get_registry_direct(registry_package_id)
        df_registry = extract_registry_to_df(raw_registry)
        df_registry_clean = clean_and_normalize(df_registry)

        raw_ear = get_ear_data_direct(ear_package_id, start_date=start_date, end_date=end_date, page_size=10000)
        df_ear = extract_ear_to_df(raw_ear)
        df_ear_clean = clean_and_normalize(df_ear, date_col="ear_data" if "ear_data" in df_ear.columns else None)

        raw_hydro = get_hydro_data_direct(hydro_package_id, start_date=start_date, end_date=end_date, page_size=10000)
        df_hydro = extract_hydro_to_df(raw_hydro)
        df_hydro_clean = clean_and_normalize(df_hydro, date_col="din_instante" if "din_instante" in df_hydro.columns else None)

        df_final = aggregate_ear_hydro_registry(df_ear_clean, df_hydro_clean, df_registry_clean)
        
        df_weather = fetch_weather_batch(df_final, start_date=start_date, end_date=end_date, max_workers=5)

        df_final = pd.merge(
            df_final,
            df_weather,
            on=["id_reservatorio", "ear_data"],
            how="left"
        )

        today = datetime.now().strftime("%Y-%m-%d")
        df_final['processed_date'] = today
        df_final['partition_date'] = today
        
        logger.info(f"DataFrame final tem {len(df_final)} registros")
        
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_csv:
            df_final.to_csv(temp_csv.name, index=False, encoding="utf-8", sep=",")
            temp_csv_path = temp_csv.name
            
        logger.info(f"CSV temporário salvo: {temp_csv_path}")

        # Envia para GCS
        bucket_name = "sauter_university"
        gcs_blob_name = f"Data_Engineering/processed/date={today}/processed_dataset.csv"
        gcs_url = upload_to_gcs(bucket_name, temp_csv_path, gcs_blob_name)
        
        logger.info(f"Arquivo enviado para GCS: {gcs_url}")

        # Carrega no BigQuery
        bigquery_result = None
        if load_to_bigquery:
            try:
                logger.info("Iniciando carregamento no BigQuery...")
                bq_service = BigQueryService()
                gcs_uri = f"gs://{bucket_name}/{gcs_blob_name}"
                
                bigquery_result = bq_service.load_pipeline_data(
                    gcs_uri=gcs_uri,
                    sample_df=df_final
                )
                logger.info("Dados carregados no BigQuery com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar no BigQuery: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                bigquery_result = {"error": str(e)}

        os.remove(temp_csv_path)
        logger.info("Arquivo temporário removido")

        return JSONResponse(
            status_code=200,
            content={
                "message": "Pipeline executada com sucesso",
                "gcs_url": gcs_url,
                "rows": len(df_final),
                "partition_date": today,
                "file_path": gcs_blob_name,
                "bigquery_result": bigquery_result
            }
        )
        
    except Exception as e:
        error_message = str(e)
        error_traceback = traceback.format_exc()
        
        logger.error(f"Erro na execução do pipeline: {error_message}")
        logger.error(f"Traceback completo: {error_traceback}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": error_message,
                "traceback": error_traceback if logger.level <= logging.DEBUG else None
            }
        )