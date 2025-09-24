from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class BigQueryService:
    def __init__(self, project_id: str = None, dataset_id: str = None):
        self.project_id = project_id or "graphite-byte-472516-n8"
        self.dataset_id = dataset_id or "SauterUniversity"
        self.table_name = "processed_reservatorios"
        self.client = bigquery.Client(project=self.project_id)
        logger.info(f"BigQuery configurado: {self.project_id}.{self.dataset_id}.{self.table_name}")
    
    def load_pipeline_data(self, gcs_uri: str, sample_df: pd.DataFrame = None):
        """
        Carrega dados do GCS para BigQuery de forma simples e robusta
        """
        try:
            logger.info(f"Iniciando load para: {gcs_uri}")
            
            # Garantir que dataset existe
            dataset_ref = f"{self.project_id}.{self.dataset_id}"
            try:
                self.client.get_dataset(dataset_ref)
                logger.info(f"Dataset {dataset_ref} já existe")
            except NotFound:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "US"  # ou "southamerica-east1" para Brasil
                dataset = self.client.create_dataset(dataset)
                logger.info(f"Dataset {dataset_ref} criado")
            
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_name}"
            
            # Verificar se tabela existe
            table_exists = False
            try:
                table = self.client.get_table(table_ref)
                table_exists = True
                logger.info(f"Tabela existe com {table.num_rows} registros - usando schema existente")
            except NotFound:
                logger.info("Tabela não existe - será criada automaticamente")
            
            # Configuração: autodetect apenas se tabela NÃO existir
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,
                field_delimiter=",",
                autodetect=not table_exists,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                allow_jagged_rows=True,
                allow_quoted_newlines=True,
                ignore_unknown_values=table_exists
            )
            
            logger.info(f"Job config: autodetect={not table_exists}, write_disposition=APPEND")
            
            # Se tabela não existe E temos sample_df, tentar adicionar particionamento
            if not table_exists and sample_df is not None and 'partition_date' in sample_df.columns:
                logger.info("Adicionando particionamento por partition_date")
                job_config.time_partitioning = bigquery.TimePartitioning(
                    type_=bigquery.TimePartitioningType.DAY,
                    field="partition_date"
                )
            
            # Executar load job
            logger.info(f"Iniciando load job: {gcs_uri} -> {table_ref}")
            load_job = self.client.load_table_from_uri(gcs_uri, table_ref, job_config=job_config)
            
            # Aguardar conclusão
            logger.info("Aguardando conclusão do load job...")
            load_job.result(timeout=300)
            
            # Verificar erros
            if load_job.errors:
                logger.error(f"Erros no load job: {load_job.errors}")
                raise Exception(f"Load job falhou: {load_job.errors}")
            
            # Obter estatísticas finais
            table = self.client.get_table(table_ref)
            
            result = {
                "table_id": table_ref,
                "rows_loaded": load_job.output_rows,
                "total_rows": table.num_rows,
                "created_table": not table_exists,
                "job_id": load_job.job_id
            }
            
            logger.info(f"Load concluído: {load_job.output_rows} linhas carregadas, total: {table.num_rows}")
            return result
            
        except Exception as e:
            logger.error(f"Erro no BigQuery load: {str(e)}")
            raise

    def get_table_info(self):
        """Retorna informações sobre a tabela (método seguro)"""
        try:
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_name}"
            table = self.client.get_table(table_ref)
            
            return {
                "table_id": table.table_id,
                "full_table_name": table_ref,
                "num_rows": table.num_rows,
                "num_bytes": table.num_bytes,
                "created": table.created.isoformat() if table.created else None,
                "modified": table.modified.isoformat() if table.modified else None,
                "schema": [{"name": field.name, "type": field.field_type} for field in table.schema]
            }
        except NotFound:
            return {"message": "Tabela não existe"}
        except Exception as e:
            logger.error(f"Erro ao obter informações da tabela: {str(e)}")
            raise

    def delete_table(self):
        """Deleta tabela (para casos de emergência)"""
        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_name}"
        try:
            self.client.delete_table(table_ref)
            logger.info(f"Tabela {table_ref} deletada")
            return True
        except NotFound:
            logger.info(f"Tabela {table_ref} não existia")
            return False