import unittest
from unittest.mock import patch, MagicMock

from app.services.weather_service import get_weather_data

class TestWeatherService(unittest.TestCase):

    @patch('app.services.weather_service.requests.get')
    def test_get_weather_data_success(self, mock_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        expected_json = {"daily": {"time": ["2023-01-01"], "temperature_2m_max": [25.0]}}
        mock_response.json.return_value = expected_json
        mock_get.return_value = mock_response

        lat, lon = -23.55, -46.63
        start, end = "2023-01-01", "2023-01-01"

        # Act
        result = get_weather_data(lat, lon, start, end)

        # Assert
        expected_url = (
            "https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={lat}&longitude={lon}"
            f"&start_date={start}&end_date={end}"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            "&timezone=America/Sao_Paulo"
        )
        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(result, expected_json)

    @patch('app.services.weather_service.requests.get')
    def test_get_weather_data_failure(self, mock_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        lat, lon = -23.55, -46.63
        start, end = "2023-01-01", "2023-01-01"

        # Act
        result = get_weather_data(lat, lon, start, end)

        # Assert
        expected_result = {"error": "Não foi possível obter os dados meteorológicos", "status_code": 500}
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
