import os
import pandas as pd
import io
from datetime import datetime
from google.cloud import storage
from typing import Dict


def upload_parquet_to_gcs(parquet_bytes: bytes, dataset_name: str, original_filename: str) -> Dict:
    bucket_name = "sauter_university"
    project_id = os.getenv("GCP_PROJECT_ID", "seu-project-id-aqui")
    
    # Data de hoje para versionamento
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Validar se é um parquet válido lendo os bytes
    try:
        # Ler o parquet direto dos bytes para validar
        df = pd.read_parquet(io.BytesIO(parquet_bytes))
        records_count = len(df)
        
        if df.empty:
            raise ValueError("Arquivo parquet está vazio")
            
    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo parquet: {str(e)}")
    
    # Criar caminho no bucket
    timestamp = datetime.now().strftime("%H%M%S")
    file_path = f"Data_Engineering/processed/{dataset_name}/{today}/{timestamp}_{original_filename}"
    
    # Inicializar cliente GCS
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    
    # Upload direto dos bytes para o GCS
    blob.upload_from_string(
        parquet_bytes,
        content_type='application/octet-stream'
    )
    
    print(f"✓ Arquivo enviado: gs://{bucket_name}/{file_path}")
    
    return {
        "file_path": f"gs://{bucket_name}/{file_path}",
        "upload_date": today,
        "records_count": records_count,
        "file_size_bytes": len(parquet_bytes)
    }