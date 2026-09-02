import pytest

from app.api.deps import get_centre_repository, get_current_farmer_uid, get_slot_booking_repository
from app.core.config import Settings
from app.core.exceptions import AppError, ServiceUnavailableError, UnauthorizedError
from app.core.firebase import FirebaseState
from app.core.secrets import get_aadhaar_hmac_key


class _UnconfiguredFirebase(FirebaseState):
    @property
    def is_configured(self) -> bool:
        return False


class _UnavailableFirestore(_UnconfiguredFirebase):
    def firestore_client(self) -> None:
        return None


def test_missing_authorization_header_rejected():
    settings = Settings(environment="development")
    with pytest.raises(UnauthorizedError):
        get_current_farmer_uid(authorization="", settings=settings, firebase=_UnconfiguredFirebase())


def test_dev_fallback_is_disabled_by_default():
    settings = Settings(environment="development")
    assert settings.allow_dev_auth_fallback is False


def test_aadhaar_hmac_key_requires_secret_manager_configuration():
    with pytest.raises(AppError) as exc_info:
        get_aadhaar_hmac_key(Settings(aadhaar_hmac_secret_name=""))

    assert exc_info.value.status_code == 503


def test_aadhaar_hmac_key_is_retrieved_from_secret_manager(monkeypatch):
    expected_key = b"a" * 32
    monkeypatch.setattr("app.core.secrets._access_secret", lambda name: expected_key)

    key = get_aadhaar_hmac_key(
        Settings(
            aadhaar_hmac_secret_name=(
                "projects/test-project/secrets/aadhaar-hmac-key/versions/7"
            )
        )
    )

    assert key == expected_key


def test_aadhaar_hmac_key_rejects_mutable_latest_alias(monkeypatch):
    monkeypatch.setattr("app.core.secrets._access_secret", lambda name: b"a" * 32)

    with pytest.raises(AppError) as exc_info:
        get_aadhaar_hmac_key(
            Settings(
                aadhaar_hmac_secret_name=(
                    "projects/test-project/secrets/aadhaar-hmac-key/versions/latest"
                )
            )
        )

    assert exc_info.value.status_code == 503


def test_aadhaar_hmac_key_rejects_malformed_resource_name(monkeypatch):
    monkeypatch.setattr("app.core.secrets._access_secret", lambda name: b"a" * 32)

    with pytest.raises(AppError) as exc_info:
        get_aadhaar_hmac_key(Settings(aadhaar_hmac_secret_name="not-a-resource-name"))

    assert exc_info.value.status_code == 503


def test_malformed_authorization_header_rejected():
    settings = Settings(environment="development")
    with pytest.raises(UnauthorizedError):
        get_current_farmer_uid(
            authorization="Token abc", settings=settings, firebase=_UnconfiguredFirebase()
        )


def test_dev_fallback_accepts_bearer_token_as_uid():
    settings = Settings(environment="development", allow_dev_auth_fallback=True)
    uid = get_current_farmer_uid(
        authorization="Bearer some-token", settings=settings, firebase=_UnconfiguredFirebase()
    )
    assert uid == "some-token"


def test_bearer_scheme_is_case_insensitive():
    settings = Settings(environment="development", allow_dev_auth_fallback=True)
    uid = get_current_farmer_uid(
        authorization="bearer some-token", settings=settings, firebase=_UnconfiguredFirebase()
    )
    assert uid == "some-token"

    uid = get_current_farmer_uid(
        authorization="BEARER some-token", settings=settings, firebase=_UnconfiguredFirebase()
    )
    assert uid == "some-token"


def test_unconfigured_firebase_rejected_outside_dev_fallback():
    settings = Settings(environment="production", allow_dev_auth_fallback=False)
    with pytest.raises(UnauthorizedError):
        get_current_farmer_uid(
            authorization="Bearer some-token", settings=settings, firebase=_UnconfiguredFirebase()
        )


def test_slot_repository_uses_memory_only_in_development():
    repository = get_slot_booking_repository(
        firebase=_UnavailableFirestore(), settings=Settings(environment="development")
    )

    assert repository.__class__.__name__ == "InMemorySlotBookingRepository"


def test_slot_repository_fails_closed_when_firestore_is_unavailable_in_production():
    with pytest.raises(ServiceUnavailableError):
        get_slot_booking_repository(
            firebase=_UnavailableFirestore(), settings=Settings(environment="production")
        )


def test_centre_repository_uses_memory_only_in_development():
    repository = get_centre_repository(
        firebase=_UnavailableFirestore(), settings=Settings(environment="development")
    )

    assert repository.__class__.__name__ == "InMemoryCentreRepository"


def test_centre_repository_fails_closed_when_firestore_is_unavailable_in_production():
    with pytest.raises(ServiceUnavailableError):
        get_centre_repository(
            firebase=_UnavailableFirestore(), settings=Settings(environment="production")
        )
