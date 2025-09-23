import unittest
from unittest.mock import patch, MagicMock
from app.services.gcs_service import upload_to_gcs

class TestGcsService(unittest.TestCase):

    @patch('google.cloud.storage.Client')
    def test_upload_to_gcs_with_credentials(self, mock_storage_client):
        # Arrange
        mock_client_instance = MagicMock()
        mock_storage_client.from_service_account_json.return_value = mock_client_instance

        mock_bucket = MagicMock()
        mock_client_instance.bucket.return_value = mock_bucket

        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        bucket_name = "test-bucket"
        source_file_path = "/tmp/test-file.txt"
        destination_blob_name = "test-blob"
        credentials_path = "/path/to/creds.json"

        # Act
        result = upload_to_gcs(bucket_name, source_file_path, destination_blob_name, credentials_path)

        # Assert
        mock_storage_client.from_service_account_json.assert_called_once_with(credentials_path)
        mock_client_instance.bucket.assert_called_once_with(bucket_name)
        mock_bucket.blob.assert_called_once_with(destination_blob_name)
        mock_blob.upload_from_filename.assert_called_once_with(source_file_path)
        self.assertEqual(result, f"File {source_file_path} uploaded to {bucket_name}/{destination_blob_name}.")

    @patch('google.cloud.storage.Client')
    def test_upload_to_gcs_without_credentials(self, mock_storage_client):
        # Arrange
        mock_client_instance = MagicMock()
        mock_storage_client.return_value = mock_client_instance

        mock_bucket = MagicMock()
        mock_client_instance.bucket.return_value = mock_bucket

        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        bucket_name = "test-bucket"
        source_file_path = "/tmp/test-file.txt"
        destination_blob_name = "test-blob"

        # Act
        result = upload_to_gcs(bucket_name, source_file_path, destination_blob_name)

        # Assert
        mock_storage_client.assert_called_once()
        mock_client_instance.bucket.assert_called_once_with(bucket_name)
        mock_bucket.blob.assert_called_once_with(destination_blob_name)
        mock_blob.upload_from_filename.assert_called_once_with(source_file_path)
        self.assertEqual(result, f"File {source_file_path} uploaded to {bucket_name}/{destination_blob_name}.")

if __name__ == '__main__':
    unittest.main()
