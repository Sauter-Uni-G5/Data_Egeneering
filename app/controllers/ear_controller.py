import logging
import pandas as pd
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import Optional

from app.services.ear_service import (
    fetch_package_metadata,
    find_parquet_url,
    read_parquet_from_url,
    records_from_dataframe
)

router = APIRouter(prefix="/data/ear", tags=["EAR"])


@router.get("/")
def get_ear_data(
    package_id: str = Query(...),
    ano: Optional[int] = Query(None),
    mes: Optional[int] = Query(None),
    nome_reservatorio: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(100)
):
    try:
        metadata = fetch_package_metadata(package_id)

        if start_date and end_date:
            start_ts, end_ts = pd.to_datetime(start_date), pd.to_datetime(end_date)
            years = list(range(start_ts.year, end_ts.year + 1))
        elif ano:
            years = [ano]
            start_ts = end_ts = None
        else:
            return JSONResponse({"error": "Informe 'ano' ou 'start_date'/'end_date'."}, status_code=400)

        df_list = [
            read_parquet_from_url(find_parquet_url(metadata, y))
            for y in years
            if find_parquet_url(metadata, y)
        ]
        if not df_list:
            return JSONResponse({"error": "Nenhum parquet encontrado para os anos requisitados."}, status_code=404)

        df = pd.concat(df_list, ignore_index=True)

        if "ear_data" in df.columns:
            df["ear_data"] = pd.to_datetime(df["ear_data"], errors="coerce", dayfirst=True)

            if start_date and end_date:
                df = df[(df["ear_data"] >= start_ts) & (df["ear_data"] <= end_ts)]
            else:
                if mes:
                    df = df[(df["ear_data"].dt.year == ano) & (df["ear_data"].dt.month == mes)]
                else:
                    df = df[df["ear_data"].dt.year == ano]

        if nome_reservatorio:
            df = df[df["nom_reservatorio"].astype(str).str.contains(nome_reservatorio, case=False, na=False)]

        start_idx = (page - 1) * page_size
        page_df = df.iloc[start_idx:start_idx + page_size]
        has_more = len(df) > start_idx + page_size

        records = records_from_dataframe(page_df)
        return JSONResponse({"page": page, "page_size": page_size, "has_more": has_more, "data": records})

    except Exception as e:
        logging.exception("Erro processando requisição")
        return JSONResponse({"error": str(e)}, status_code=500)
