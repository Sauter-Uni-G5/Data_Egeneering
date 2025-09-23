import unittest
from unittest.mock import patch, MagicMock, call
import pandas as pd
from fastapi.responses import JSONResponse

from app.services.ons_service import (
    fetch_package_metadata,
    find_parquet_url,
    read_parquet_from_url,
    get_reservoir_data,
    records_from_dataframe,
)

class TestOnsService(unittest.TestCase):

    def setUp(self):
        # Clear cache before each test to ensure isolation
        fetch_package_metadata.cache_clear()

    @patch('app.services.ons_service._session.get')
    def test_fetch_package_metadata_success(self, mock_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "result": {"id": "123", "name": "Test Package"}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Act
        result = fetch_package_metadata("test_id")

        # Assert
        self.assertEqual(result, {"id": "123", "name": "Test Package"})
        mock_get.assert_called_once()

    @patch('app.services.ons_service._session.get')
    def test_fetch_package_metadata_api_error(self, mock_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": False}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Act & Assert
        with self.assertRaises(ValueError):
            fetch_package_metadata("test_id")

    def test_find_parquet_url(self):
        # Arrange
        metadata = {
            "resources": [
                {"name": "data-2022.csv", "format": "CSV", "url": "http://example.com/data-2022.csv"},
                {"name": "data-2023.parquet", "format": "PARQUET", "url": "http://example.com/data-2023.parquet"},
                {"name": "data-2024.parquet", "format": "PARQUET", "url": "http://example.com/data-2024.parquet"},
            ]
        }
        # Act & Assert
        self.assertEqual(find_parquet_url(metadata, 2024), "http://example.com/data-2024.parquet")
        self.assertEqual(find_parquet_url(metadata, 2021), "http://example.com/data-2023.parquet") # Fallback to first
        self.assertEqual(find_parquet_url(metadata), "http://example.com/data-2023.parquet") # No year
        self.assertIsNone(find_parquet_url({"resources": []}))

    @patch('pandas.read_parquet')
    def test_read_parquet_from_url_success(self, mock_read_parquet):
        # Arrange
        mock_df = pd.DataFrame({'a': [1, 2]})
        mock_read_parquet.return_value = mock_df

        # Act
        df = read_parquet_from_url("http://fake.url/data.parquet")

        # Assert
        self.assertTrue(df.equals(mock_df))
        mock_read_parquet.assert_called_once_with("http://fake.url/data.parquet", engine="pyarrow")

    def test_records_from_dataframe(self):
        # Arrange
        data = {'col1': [1, 2], 'col2': [0.1, None], 'col3': ['a', ' b ']}
        df = pd.DataFrame(data)

        # Act
        records = records_from_dataframe(df)

        # Assert
        expected = [
            {'col1': 1, 'col2': 0.1, 'col3': 'a'},
            {'col1': 2, 'col2': None, 'col3': 'b'},
        ]
        self.assertEqual(records, expected)

    @patch('app.services.ons_service.fetch_package_metadata')
    @patch('app.services.ons_service.find_parquet_url')
    @patch('app.services.ons_service.read_parquet_from_url')
    def test_get_reservoir_data_success(self, mock_read_parquet, mock_find_url, mock_fetch_meta):
        # Arrange
        mock_fetch_meta.return_value = {"id": "meta"}
        mock_find_url.return_value = "http://fake.url/2023.parquet"

        df = pd.DataFrame({'data': pd.to_datetime(['2023-01-15', '2023-02-10']), 'val': [10, 20]})
        mock_read_parquet.return_value = df

        # Act - date range is within 2023, so only one year is processed
        response = get_reservoir_data("pkg_id", None, None, None, "2023-01-01", "2023-12-31", 1, 10)

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 200)

        body = response.body.decode()
        self.assertIn('"page":1', body)
        self.assertIn('"has_more":false', body)
        self.assertIn('"val":10', body)
        self.assertIn('"val":20', body)

        mock_fetch_meta.assert_called_once_with("pkg_id")
        mock_find_url.assert_called_once_with({"id": "meta"}, 2023)
        mock_read_parquet.assert_called_once_with("http://fake.url/2023.parquet")

if __name__ == '__main__':
    unittest.main()
