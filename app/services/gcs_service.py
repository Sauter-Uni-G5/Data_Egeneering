from google.cloud import storage

def upload_to_gcs(bucket_name: str, source_file_path: str, destination_blob_name: str, credentials_path: str = None):
    if credentials_path:
        client = storage.Client.from_service_account_json(credentials_path)
    else:
        client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_path)
    return f"File {source_file_path} uploaded to {bucket_name}/{destination_blob_name}."