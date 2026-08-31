VALID_PAYLOAD = {
    "full_name": "Ravi Kumar",
    "phone_number": "9876543210",
    "aadhaar_number": "123456789012",
    "village": "Rajpur",
    "district": "Solapur",
    "state": "Maharashtra",
    "preferred_language": "mr",
}


def test_register_farmer_success(client, auth_headers):
    response = client.post("/api/v1/farmers/register", json=VALID_PAYLOAD, headers=auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["full_name"] == "Ravi Kumar"
    assert body["aadhaar_last4"] == "9012"
    assert "aadhaar_number" not in body  # full number must never be returned


def test_register_farmer_duplicate_conflicts(client, auth_headers):
    client.post("/api/v1/farmers/register", json=VALID_PAYLOAD, headers=auth_headers)
    response = client.post("/api/v1/farmers/register", json=VALID_PAYLOAD, headers=auth_headers)
    assert response.status_code == 409


def test_register_farmer_invalid_aadhaar(client, auth_headers):
    payload = {**VALID_PAYLOAD, "aadhaar_number": "123"}
    response = client.post("/api/v1/farmers/register", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_register_farmer_invalid_phone(client, auth_headers):
    payload = {**VALID_PAYLOAD, "phone_number": "12345"}
    response = client.post("/api/v1/farmers/register", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_get_profile_requires_registration_first(client, auth_headers):
    response = client.get("/api/v1/farmers/me", headers=auth_headers)
    assert response.status_code == 404


def test_get_profile_after_registration(client, auth_headers):
    client.post("/api/v1/farmers/register", json=VALID_PAYLOAD, headers=auth_headers)
    response = client.get("/api/v1/farmers/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["village"] == "Rajpur"


def test_update_profile(client, auth_headers):
    client.post("/api/v1/farmers/register", json=VALID_PAYLOAD, headers=auth_headers)
    response = client.patch(
        "/api/v1/farmers/me", json={"village": "Pandharpur"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["village"] == "Pandharpur"
    # Untouched fields survive the partial update.
    assert response.json()["full_name"] == "Ravi Kumar"
