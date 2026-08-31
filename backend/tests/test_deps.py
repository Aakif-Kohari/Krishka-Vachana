import pytest

from app.api.deps import get_current_farmer_uid
from app.core.config import Settings
from app.core.exceptions import UnauthorizedError
from app.core.firebase import FirebaseState


class _UnconfiguredFirebase(FirebaseState):
    @property
    def is_configured(self) -> bool:
        return False


def test_missing_authorization_header_rejected():
    settings = Settings(environment="development")
    with pytest.raises(UnauthorizedError):
        get_current_farmer_uid(authorization="", settings=settings, firebase=_UnconfiguredFirebase())


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


def test_unconfigured_firebase_rejected_outside_dev_fallback():
    settings = Settings(environment="production", allow_dev_auth_fallback=False)
    with pytest.raises(UnauthorizedError):
        get_current_farmer_uid(
            authorization="Bearer some-token", settings=settings, firebase=_UnconfiguredFirebase()
        )
