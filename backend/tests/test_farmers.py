import hashlib
from concurrent.futures import ThreadPoolExecutor

from app.api import deps
from app.core.exceptions import ConflictError
from app.main import app
from app.repositories.memory import InMemoryFarmerRepository
from app.schemas.farmer import FarmerCreate
from app.services.farmer_service import register_farmer


VALID_PAYLOAD = {
    "full_name": "Ravi Kumar",
    "phone_number": "9876543210",
    "aadhaar_number": "123456789012",
    "village": "Rajpur",
    "district": "Solapur",
    "state": "Maharashtra",
    "preferred_language": "mr",
}


def test_register_farmer_success(client, auth_headers, farmer_repo):
    response = client.post("/api/v1/farmers/register", json=VALID_PAYLOAD, headers=auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["full_name"] == "Ravi Kumar"
    assert body["aadhaar_last4"] == "9012"
    assert "aadhaar_number" not in body  # full number must never be returned
    stored = farmer_repo.get(body["farmer_id"])
    assert stored["aadhaar_hash"].startswith("hmac-sha256:v1:")
    assert stored["aadhaar_hash"] != hashlib.sha256(b"123456789012").hexdigest()


def test_register_farmer_duplicate_conflicts(client, auth_headers):
    client.post("/api/v1/farmers/register", json=VALID_PAYLOAD, headers=auth_headers)
    response = client.post("/api/v1/farmers/register", json=VALID_PAYLOAD, headers=auth_headers)
    assert response.status_code == 409


def test_register_farmer_rejects_duplicate_aadhaar_for_another_account(client, auth_headers):
    client.post("/api/v1/farmers/register", json=VALID_PAYLOAD, headers=auth_headers)
    app.dependency_overrides[deps.get_current_farmer_uid] = lambda: "another-farmer-uid"

    response = client.post("/api/v1/farmers/register", json=VALID_PAYLOAD, headers=auth_headers)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_concurrent_registration_reserves_aadhaar_once():
    repo = InMemoryFarmerRepository()
    payload = FarmerCreate(**VALID_PAYLOAD)

    def register(farmer_id):
        try:
            return register_farmer(repo, farmer_id, payload, b"test-key")
        except ConflictError:
            return None

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(register, ["farmer-one", "farmer-two"]))

    assert sum(result is not None for result in results) == 1
    created = sum(
        repo.get(farmer_id) is not None for farmer_id in ["farmer-one", "farmer-two"]
    )
    assert created == 1


def test_concurrent_registration_for_same_farmer_does_not_orphan_aadhaar():
    repo = InMemoryFarmerRepository()
    payloads = [
        FarmerCreate(**VALID_PAYLOAD),
        FarmerCreate(**{**VALID_PAYLOAD, "aadhaar_number": "987654321098"}),
    ]

    def register(payload):
        try:
            return register_farmer(repo, "shared-farmer", payload, b"test-key")
        except ConflictError:
            return None

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(register, payloads))

    assert sum(result is not None for result in results) == 1
    losing_payload = payloads[results.index(None)]
    assert register_farmer(repo, "another-farmer", losing_payload, b"test-key") is not None


def test_register_farmer_migrates_matching_legacy_hash(client, auth_headers, farmer_repo):
    legacy_hash = hashlib.sha256(VALID_PAYLOAD["aadhaar_number"].encode("utf-8")).hexdigest()
    farmer_repo.create(
        "legacy-farmer-uid",
        {
            "aadhaar_hash": legacy_hash,
            "aadhaar_last4": "9012",
        },
    )

    response = client.post("/api/v1/farmers/register", json=VALID_PAYLOAD, headers=auth_headers)

    assert response.status_code == 409
    migrated = farmer_repo.get("legacy-farmer-uid")
    assert migrated["aadhaar_hash"].startswith("hmac-sha256:v1:")
    assert migrated["aadhaar_hash"] != legacy_hash


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
