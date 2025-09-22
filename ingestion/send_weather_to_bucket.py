import os
import requests
import pandas as pd
from datetime import datetime
from google.cloud import storage

def fetch_weather_data(api_url: str) -> pd.DataFrame:
    response = requests.get(api_url)
    response.raise_for_status()
    return pd.DataFrame(response.json())

def save_to_gcs(df: pd.DataFrame, bucket_name: str, project_id: str, year: str, month: str):
    # Data da ingestão (quando coletamos)
    ingestion_date = datetime.utcnow().strftime("%Y-%m-%d")

    # Nome do arquivo (ex: january.parquet)
    month_name = pd.to_datetime(month, format="%m").strftime("%B").lower()
    file_path = f"Data_Engineering/weather_raw_data/ingestion_date={ingestion_date}/year={year}/{month_name}.parquet"

    # Salvar localmente em parquet
    local_file = "/tmp/temp.parquet"
    df.to_parquet(local_file, engine="pyarrow", index=False)

    # Upload para GCS
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.upload_from_filename(local_file)

    print(f"Arquivo salvo em: gs://{bucket_name}/{file_path}")

if __name__ == "__main__":
    # Exemplo de chamada da sua API
    api_url = "https://ml-api-lfsox4zmrq-uc.a.run.app/api/data/weather?latitude=-2.5&longitude=-46.6&start_date=2000-01-01&end_date=2000-01-31"
    
    # Coleta
    df = fetch_weather_data(api_url)

    # Pega ano e mês dos dados coletados
    df["date"] = pd.to_datetime(df["date"])  # supondo que tem a coluna "date"
    year = str(df["date"].dt.year.min())
    month = str(df["date"].dt.month.min()).zfill(2)

    # Salva no GCS
    save_to_gcs(df, bucket_name="sauter_university", project_id="SEU_PROJECT_ID", year=year, month=month)
