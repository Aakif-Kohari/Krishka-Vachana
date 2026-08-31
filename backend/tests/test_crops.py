FARMER_PAYLOAD = {
    "full_name": "Ravi Kumar",
    "phone_number": "9876543210",
    "aadhaar_number": "123456789012",
    "village": "Rajpur",
    "district": "Solapur",
    "state": "Maharashtra",
    "preferred_language": "mr",
}


def _register_farmer(client, auth_headers):
    client.post("/api/v1/farmers/register", json=FARMER_PAYLOAD, headers=auth_headers)


def test_register_crop_requires_farmer_profile_first(client, auth_headers):
    response = client.post(
        "/api/v1/crops", json={"crop_type": "wheat", "quantity_quintals": 12}, headers=auth_headers
    )
    assert response.status_code == 404


def test_register_crop_success(client, auth_headers):
    _register_farmer(client, auth_headers)
    response = client.post(
        "/api/v1/crops", json={"crop_type": "wheat", "quantity_quintals": 18.5}, headers=auth_headers
    )
    assert response.status_code == 201
    body = response.json()
    assert body["crop_type"] == "wheat"
    assert body["quantity_quintals"] == 18.5


def test_register_crop_invalid_quantity(client, auth_headers):
    _register_farmer(client, auth_headers)
    response = client.post(
        "/api/v1/crops", json={"crop_type": "wheat", "quantity_quintals": 0}, headers=auth_headers
    )
    assert response.status_code == 422
    assert response.json() == {
        "error": {"code": "validation_error", "message": "Request validation failed"}
    }


def test_register_crop_other_requires_label(client, auth_headers):
    _register_farmer(client, auth_headers)
    response = client.post(
        "/api/v1/crops", json={"crop_type": "other", "quantity_quintals": 5}, headers=auth_headers
    )
    assert response.status_code == 422


def test_register_crop_other_rejects_blank_label(client, auth_headers):
    _register_farmer(client, auth_headers)
    response = client.post(
        "/api/v1/crops",
        json={"crop_type": "other", "crop_type_other": "   ", "quantity_quintals": 5},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_register_crop_other_persists_trimmed_label(client, auth_headers):
    _register_farmer(client, auth_headers)
    response = client.post(
        "/api/v1/crops",
        json={"crop_type": "other", "crop_type_other": "  lentils  ", "quantity_quintals": 5},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["crop_type_other"] == "lentils"


def test_list_crops_for_farmer(client, auth_headers):
    _register_farmer(client, auth_headers)
    client.post("/api/v1/crops", json={"crop_type": "wheat", "quantity_quintals": 10}, headers=auth_headers)
    client.post("/api/v1/crops", json={"crop_type": "paddy", "quantity_quintals": 5}, headers=auth_headers)

    response = client.get("/api/v1/crops/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {c["crop_type"] for c in body} == {"wheat", "paddy"}
