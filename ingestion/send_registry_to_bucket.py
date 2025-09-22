import os
import requests
import pandas as pd
from datetime import datetime
from google.cloud import storage
import json
from typing import Dict, Any

def fetch_registry_data(base_url: str, package_id: str) -> Dict[Any, Any]:
    """
    Faz requisição para o endpoint de registry
    """
    url = f"{base_url}/data/registry"
    params = {"package_id": package_id}
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def process_registry_data(raw_data: Dict[Any, Any]) -> pd.DataFrame:
    """
    Processa os dados brutos do registry e converte para DataFrame
    """
    # Se os dados vierem como lista diretamente
    if isinstance(raw_data, list):
        df = pd.DataFrame(raw_data)
    # Se vierem dentro de uma chave específica
    elif isinstance(raw_data, dict):
        # Adapte conforme a estrutura real dos seus dados
        if 'data' in raw_data:
            df = pd.DataFrame(raw_data['data'])
        elif 'results' in raw_data:
            df = pd.DataFrame(raw_data['results'])
        else:
            # Se for um objeto único, transforma em lista
            df = pd.DataFrame([raw_data])
    else:
        raise ValueError("Formato de dados não reconhecido")
    
    return df

def create_monthly_partitions(df: pd.DataFrame, date_column: str = None) -> Dict[str, pd.DataFrame]:
    """
    Separa o DataFrame em partições mensais
    Se não houver coluna de data, cria uma partição única para o mês atual
    """
    partitions = {}
    
    if date_column and date_column in df.columns:
        # Se existe coluna de data, particiona por mês
        df[date_column] = pd.to_datetime(df[date_column])
        df['year'] = df[date_column].dt.year
        df['month'] = df[date_column].dt.month
        
        for (year, month), group in df.groupby(['year', 'month']):
            month_name = pd.to_datetime(f"{year}-{month:02d}-01").strftime("%B").lower()
            key = f"{year}_{month_name}"
            partitions[key] = group.drop(['year', 'month'], axis=1)
    else:
        # Se não há coluna de data, usa ano/mês atual
        current_date = datetime.now()
        year = current_date.year
        month_name = current_date.strftime("%B").lower()
        key = f"{year}_{month_name}"
        partitions[key] = df
    
    return partitions

def save_partition_to_gcs(df: pd.DataFrame, bucket_name: str, project_id: str, 
                         year: str, month_name: str, ingestion_date: str):
    """
    Salva uma partição no Google Cloud Storage
    """
    # Estrutura do caminho: Data_Engineering/registry_raw_data/ingestion_date=YYYY-MM-DD/year=YYYY/month_name.parquet
    file_path = f"Data_Engineering/registry_raw_data/ingestion_date={ingestion_date}/year={year}/{month_name}.parquet"
    
    # Salvar localmente primeiro
    local_file = f"/tmp/registry_{year}_{month_name}.parquet"
    df.to_parquet(local_file, engine="pyarrow", index=False)
    
    # Upload para GCS
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    
    # Upload do arquivo
    blob.upload_from_filename(local_file)
    
    # Limpar arquivo temporário
    os.remove(local_file)
    
    print(f"Arquivo salvo em: gs://{bucket_name}/{file_path}")
    return file_path

def save_registry_to_gcs(df: pd.DataFrame, bucket_name: str, project_id: str, 
                        date_column: str = None):
    """
    Salva os dados do registry no GCS com particionamento mensal
    """
    # Data da ingestão
    ingestion_date = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Criar partições mensais
    partitions = create_monthly_partitions(df, date_column)
    
    uploaded_files = []
    
    for partition_key, partition_df in partitions.items():
        year, month_name = partition_key.split('_', 1)
        
        # Salvar partição
        file_path = save_partition_to_gcs(
            partition_df, bucket_name, project_id, 
            year, month_name, ingestion_date
        )
        uploaded_files.append(file_path)
    
    return uploaded_files

def ingest_registry_data(base_url: str, package_id: str, bucket_name: str, 
                        project_id: str, date_column: str = None):
    """
    Função principal para ingestão completa dos dados de registry
    """
    print(f"Iniciando ingestão dos dados de registry para package_id: {package_id}")
    
    try:
        # 1. Buscar dados da API
        print("Buscando dados da API...")
        raw_data = fetch_registry_data(base_url, package_id)
        
        # 2. Processar dados
        print("Processando dados...")
        df = process_registry_data(raw_data)
        print(f"Dados processados: {len(df)} registros")
        
        # 3. Salvar no GCS
        print("Salvando no Google Cloud Storage...")
        uploaded_files = save_registry_to_gcs(df, bucket_name, project_id, date_column)
        
        print(f"Ingestão concluída! {len(uploaded_files)} arquivo(s) salvos:")
        for file_path in uploaded_files:
            print(f"  - {file_path}")
            
        return uploaded_files
        
    except Exception as e:
        print(f"Erro durante a ingestão: {str(e)}")
        raise

if __name__ == "__main__":
    # Configurações
    BASE_URL = "http://localhost:8000"  # Ajuste conforme sua API
    PACKAGE_ID = "seu-package-id-aqui"  # Substitua pelo package_id real
    BUCKET_NAME = "sauter_university"
    PROJECT_ID = "seu-project-id-aqui"  # Substitua pelo seu project_id
    
    # Especifique a coluna de data se existir nos dados de registry
    # Se não existir, deixe como None e será usado o mês atual
    DATE_COLUMN = None  # ou "date_column_name" se existir
    
    # Executar ingestão
    ingest_registry_data(
        base_url=BASE_URL,
        package_id=PACKAGE_ID,
        bucket_name=BUCKET_NAME,
        project_id=PROJECT_ID,
        date_column=DATE_COLUMN
    )