from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from datetime import datetime
import tempfile
import os
import pandas as pd
import logging
import traceback

from app.controllers.registry_controller import get_registry_direct
from app.controllers.ear_controller import get_ear_data_direct
from app.controllers.hydro_controller import get_hydro_data_direct
from app.pipeline.extractors.ons_extractor import (
    extract_registry_to_df, extract_ear_to_df, extract_hydro_to_df
)
from app.pipeline.transformers.data_cleaner import normalize_and_clean
from app.pipeline.transformers.aggregator import aggregate_ear_hydro_registry
from app.services.gcs_service import upload_to_gcs
from app.services.bigquery_service import BigQueryService
from app.pipeline.transformers.feature_engineering import create_lags, create_diffs, create_rolling_mean

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

        # 1. Extração dos dados
        raw_registry = get_registry_direct(registry_package_id)
        df_registry = extract_registry_to_df(raw_registry)

        raw_ear = get_ear_data_direct(ear_package_id, start_date=start_date, end_date=end_date, page_size=10000)
        df_ear = extract_ear_to_df(raw_ear)

        raw_hydro = get_hydro_data_direct(hydro_package_id, start_date=start_date, end_date=end_date, page_size=10000)
        df_hydro = extract_hydro_to_df(raw_hydro)

        # 2. Agregação (merge)
        df_final = aggregate_ear_hydro_registry(df_ear, df_hydro, df_registry)

        for col in ["val_volumeutilcon", "ear_reservatorio_percentual", "ear_total_mwmes", "val_volmax"]:
            if col in df_final.columns:
                df_final[col] = pd.to_numeric(df_final[col], errors="coerce")


        # 3. Feature engineering
        df_final = create_lags(df_final, columns="val_volumeutilcon", lag=1, groupby="id_reservatorio")
        df_final = create_lags(df_final, columns="val_volumeutilcon", lag=7, groupby="id_reservatorio")
        df_final = create_lags(df_final, columns="val_volumeutilcon", lag=14, groupby="id_reservatorio")
        df_final = create_lags(df_final, columns="val_volumeutilcon", lag=30, groupby="id_reservatorio")
        df_final = create_diffs(df_final, columns="val_volumeutilcon", periods=1, groupby="id_reservatorio")
        df_final = create_diffs(df_final, columns="val_volumeutilcon", periods=7, groupby="id_reservatorio")
        df_final = create_rolling_mean(df_final, columns="val_volumeutilcon", window=7, groupby="id_reservatorio")

        # 4. Limpeza e normalização FINAL
        df_final = normalize_and_clean(df_final)

        # 5. Remove registros sem id_reservatorio (extra segurança)
        df_final = df_final[df_final["id_reservatorio"].notnull() & (df_final["id_reservatorio"] != "")]

        today = datetime.now().strftime("%Y-%m-%d")
        df_final['processed_date'] = today
        df_final['partition_date'] = today
        logger.info(f"DataFrame final tem {len(df_final)} registros")

        print(df_final.dtypes)
        print(df_final.head(10))

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