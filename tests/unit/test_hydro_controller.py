import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

class TestHydroController(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch('app.controllers.hydro_controller.get_reservoir_data')
    def test_get_hydro_data_calls_service_with_correct_parameters(self, mock_get_reservoir_data):
        # Arrange
        mock_get_reservoir_data.return_value = {"data": "mocked_data"}

        params = {
            "package_id": "test_package_id",
            "ano": 2023,
            "mes": 10,
            "nome_reservatorio": "test_reservoir",
            "start_date": "2023-10-01",
            "end_date": "2023-10-31",
            "page": 1,
            "page_size": 10
        }

        # Act
        response = self.client.get("/api/data/hydro", params=params)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"data": "mocked_data"})
        mock_get_reservoir_data.assert_called_once_with(
            "test_package_id", 2023, 10, "test_reservoir", "2023-10-01", "2023-10-31", 1, 10
        )

if __name__ == '__main__':
    unittest.main()
