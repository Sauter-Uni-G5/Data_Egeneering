import os
from datetime import datetime
from google.cloud import storage
from typing import Dict


def upload_folder_to_gcs(folder_path: str, bucket_name: str = "sauter_university") -> Dict:
    if not os.path.isdir(folder_path):
        raise ValueError(f"O caminho fornecido não é uma pasta válida: {folder_path}")
    
    today = datetime.now().strftime("%Y-%m-%d")
    gcs_root = f"Data_Engineering/processed/{today}"
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    files_uploaded = 0

    #processed/{data_de_hoje}/{subpastas_e_arquivos}
    for root, _, files in os.walk(folder_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, folder_path)
            gcs_file_path = f"{gcs_root}/{relative_path}"  # <- melhoria aplicada
            
            blob = bucket.blob(gcs_file_path)
            blob.upload_from_filename(local_file_path)
            print(f"✓ Arquivo enviado: gs://{bucket_name}/{gcs_file_path}")
            files_uploaded += 1
    
    return {
        "folder_path": f"gs://{bucket_name}/{gcs_root}",
        "upload_date": today,
        "files_uploaded": files_uploaded
    }
