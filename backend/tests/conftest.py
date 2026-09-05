import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("OTP_HMAC_SECRET", "test-only-otp-hmac-secret-32-bytes")
os.environ["PAYMENT_GATEWAY_WEBHOOK_SECRET"] = (
    "q7L9vN2xK4mP8rT5wY1cF6hJ3sU0aB9dE2gI7kM"
)

from app.api import deps
from app.core.secrets import get_aadhaar_hmac_key
from app.main import app
from app.repositories.memory import (
    InMemoryCentreRepository,
    InMemoryCropRepository,
    InMemoryFarmerRepository,
    InMemoryQueueRepository,
    InMemorySlotBookingRepository,
)
from app.repositories.memory import InMemoryPaymentRepository

TEST_FARMER_ID = "test-farmer-uid-123"
TEST_AADHAAR_HMAC_KEY = b"test-only-aadhaar-hmac-key-32-bytes"


@pytest.fixture()
def farmer_repo():
    """Provide a fresh in-memory farmer repository for each test."""
    return InMemoryFarmerRepository()


@pytest.fixture()
def crop_repo():
    """Provide a fresh in-memory crop repository for each test."""
    return InMemoryCropRepository()


@pytest.fixture()
def centre_repo():
    """Provide a fresh in-memory centre repository for each test."""
    return InMemoryCentreRepository()


@pytest.fixture()
def booking_repo():
    """Provide a fresh in-memory booking repository for each test."""
    return InMemorySlotBookingRepository()


@pytest.fixture()
def queue_repo():
    """Provide a fresh in-memory queue repository for each test."""
    return InMemoryQueueRepository()

@pytest.fixture()
def payment_repo():
    """Provide a fresh in-memory payment repository for each test."""
    return InMemoryPaymentRepository()

@pytest.fixture()
def client(farmer_repo, crop_repo, centre_repo, booking_repo, queue_repo, payment_repo):
    """Provide a test client with dependency overrides for isolated testing."""
    app.dependency_overrides[deps.get_current_farmer_uid] = lambda: TEST_FARMER_ID
    app.dependency_overrides[deps.get_farmer_repository] = lambda: farmer_repo
    app.dependency_overrides[deps.get_crop_repository] = lambda: crop_repo
    app.dependency_overrides[deps.get_centre_repository] = lambda: centre_repo
    app.dependency_overrides[deps.get_slot_booking_repository] = lambda: booking_repo
    app.dependency_overrides[deps.get_queue_repository] = lambda: queue_repo
    app.dependency_overrides[deps.get_payment_repository] = lambda: payment_repo
    app.dependency_overrides[get_aadhaar_hmac_key] = lambda: TEST_AADHAAR_HMAC_KEY

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers():
    """Provide test authorization headers."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture()
def seeded_centre_id(centre_repo):
    """First seeded centre id - for tests that just need *a* valid centre."""
    return centre_repo.list()[0]["centre_id"]
