import pytest
from fastapi.testclient import TestClient

from app.api import deps
from app.core.secrets import get_aadhaar_hmac_key
from app.main import app
from app.repositories.memory import InMemoryCropRepository, InMemoryFarmerRepository

TEST_FARMER_ID = "test-farmer-uid-123"
TEST_AADHAAR_HMAC_KEY = b"test-only-aadhaar-hmac-key-32-bytes"


@pytest.fixture()
def farmer_repo():
    return InMemoryFarmerRepository()


@pytest.fixture()
def crop_repo():
    return InMemoryCropRepository()


@pytest.fixture()
def client(farmer_repo, crop_repo):
    app.dependency_overrides[deps.get_current_farmer_uid] = lambda: TEST_FARMER_ID
    app.dependency_overrides[deps.get_farmer_repository] = lambda: farmer_repo
    app.dependency_overrides[deps.get_crop_repository] = lambda: crop_repo
    app.dependency_overrides[get_aadhaar_hmac_key] = lambda: TEST_AADHAAR_HMAC_KEY

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers():
    return {"Authorization": "Bearer test-token"}
