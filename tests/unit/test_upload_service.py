import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.services.upload_service import upload_folder_to_gcs

class TestUploadService(unittest.TestCase):

    @patch('app.services.upload_service.os.path.isdir')
    def test_upload_folder_to_gcs_invalid_path(self, mock_isdir):
        # Arrange
        mock_isdir.return_value = False

        # Act & Assert
        with self.assertRaises(ValueError):
            upload_folder_to_gcs("/invalid/path")
        mock_isdir.assert_called_once_with("/invalid/path")

    @patch('google.cloud.storage.Client')
    @patch('app.services.upload_service.os.walk')
    @patch('app.services.upload_service.os.path.isdir')
    @patch('app.services.upload_service.datetime')
    def test_upload_folder_to_gcs_success(self, mock_datetime, mock_isdir, mock_walk, mock_storage_client):
        # Arrange
        # Mock datetime
        mock_now = datetime(2023, 10, 27)
        mock_datetime.now.return_value = mock_now
        today_str = "2023-10-27"

        # Mock os.path.isdir
        mock_isdir.return_value = True

        # Mock os.walk to simulate a directory structure
        mock_walk.return_value = [
            ('/local/folder', ['subdir'], ['file1.txt']),
            ('/local/folder/subdir', [], ['file2.txt']),
        ]

        # Mock GCS client
        mock_client_instance = MagicMock()
        mock_storage_client.return_value = mock_client_instance
        mock_bucket = MagicMock()
        mock_client_instance.bucket.return_value = mock_bucket

        # We need a new blob mock for each file
        mock_blob1 = MagicMock()
        mock_blob2 = MagicMock()
        mock_bucket.blob.side_effect = [mock_blob1, mock_blob2]

        folder_path = "/local/folder"
        bucket_name = "test-bucket"

        # Act
        result = upload_folder_to_gcs(folder_path, bucket_name)

        # Assert
        mock_isdir.assert_called_once_with(folder_path)
        mock_walk.assert_called_once_with(folder_path)
        mock_storage_client.assert_called_once()
        mock_client_instance.bucket.assert_called_once_with(bucket_name)

        # Check blob creation and upload calls
        gcs_root = f"Data_Engineering/processed/{today_str}"
        calls = mock_bucket.blob.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0].args[0], f"{gcs_root}/file1.txt")
        self.assertEqual(calls[1].args[0], f"{gcs_root}/subdir/file2.txt")

        mock_blob1.upload_from_filename.assert_called_once_with('/local/folder/file1.txt')
        mock_blob2.upload_from_filename.assert_called_once_with('/local/folder/subdir/file2.txt')

        # Check result
        self.assertEqual(result['files_uploaded'], 2)
        self.assertEqual(result['upload_date'], today_str)
        self.assertEqual(result['folder_path'], f"gs://{bucket_name}/{gcs_root}")

if __name__ == '__main__':
    unittest.main()
