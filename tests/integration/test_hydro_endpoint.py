import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_ons_service():
    with patch('app.controllers.hydro_controller.get_reservoir_data') as mock_get:
        mock_get.return_value = {"message": "Data found", "data": [{"id": 1, "value": 100}]}
        yield mock_get

def test_get_hydro_data_endpoint_success(mock_ons_service):
    # Arrange
    params = {
        "package_id": "some-valid-package-id",
        "ano": 2023
    }

    # Act
    response = client.get("/api/data/hydro", params=params)

    # Assert
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["message"] == "Data found"
    assert len(json_response["data"]) == 1
    assert json_response["data"][0]["value"] == 100
    mock_ons_service.assert_called_once_with(
        "some-valid-package-id", 2023, None, None, None, None, 1, 100
    )

def test_get_hydro_data_endpoint_missing_package_id():
    # Act
    response = client.get("/api/data/hydro")

    # Assert
    assert response.status_code == 422  # Unprocessable Entity for missing required query parameter
