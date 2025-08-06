import pytest
from fastapi.testclient import TestClient
from penguin_app.main import app

client = TestClient(app)

valid_sample = {
    "bill_length_mm": 39.1,
    "bill_depth_mm": 18.7,
    "flipper_length_mm": 181.0,
    "body_mass_g": 3750.0,
    "sex": "male",
    "island": "Torgersen"
}

def test_predict_endpoint_valid_input():
    response = client.post("/predict", json=valid_sample)
    assert response.status_code == 200
    json_data = response.json()
    assert "prediction" in json_data
    # Corrected assertion: Check for string species names, not numerical labels.
    assert json_data["prediction"] in ['Adelie', 'Chinstrap', 'Gentoo']

def test_predict_endpoint_missing_field():
    data = valid_sample.copy()
    data.pop("bill_length_mm")
    response = client.post("/predict", json=data)
    assert response.status_code == 422

def test_predict_endpoint_invalid_type():
    data = valid_sample.copy()
    data["body_mass_g"] = "not_a_number"
    response = client.post("/predict", json=data)
    assert response.status_code == 422

def test_predict_endpoint_out_of_range():
    data = valid_sample.copy()
    data["body_mass_g"] = -100
    response = client.post("/predict", json=data)
    assert response.status_code == 422

def test_predict_endpoint_empty_request():
    response = client.post("/predict", json={})
    assert response.status_code == 422

def test_predict_endpoint_invalid_enum_values():
    data = valid_sample.copy()
    data["sex"] = "unknown"
    data["island"] = "mars"
    response = client.post("/predict", json=data)
    assert response.status_code == 422