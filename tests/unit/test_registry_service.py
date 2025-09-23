import unittest
from unittest.mock import patch, MagicMock
from fastapi.responses import JSONResponse
import pandas as pd

from app.services.registry_service import get_registry_data

class TestRegistryService(unittest.TestCase):

    @patch('app.services.registry_service.fetch_package_metadata')
    @patch('app.services.registry_service.find_parquet_url')
    @patch('app.services.registry_service.read_parquet_from_url')
    @patch('app.services.registry_service.records_from_dataframe')
    def test_get_registry_data_success(self, mock_records, mock_read, mock_find, mock_fetch):
        # Arrange
        mock_fetch.return_value = {"id": "meta"}
        mock_find.return_value = "http://fake.url/data.parquet"
        mock_df = pd.DataFrame({'a': [1]})
        mock_read.return_value = mock_df
        mock_records.return_value = [{"a": 1}]

        # Act
        response = get_registry_data("test_package_id")

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body.decode(), '{"data":[{"a":1}]}')

        mock_fetch.assert_called_once_with("test_package_id")
        mock_find.assert_called_once_with({"id": "meta"})
        mock_read.assert_called_once_with("http://fake.url/data.parquet")
        mock_records.assert_called_once_with(mock_df)

    @patch('app.services.registry_service.fetch_package_metadata')
    @patch('app.services.registry_service.find_parquet_url')
    def test_get_registry_data_no_parquet_found(self, mock_find, mock_fetch):
        # Arrange
        mock_fetch.return_value = {"id": "meta"}
        mock_find.return_value = None

        # Act
        response = get_registry_data("test_package_id")

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 404)
        self.assertIn("No parquet file found", response.body.decode())

    @patch('app.services.registry_service.fetch_package_metadata')
    def test_get_registry_data_exception(self, mock_fetch):
        # Arrange
        mock_fetch.side_effect = Exception("Test error")

        # Act
        response = get_registry_data("test_package_id")

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Test error", response.body.decode())

if __name__ == '__main__':
    unittest.main()
