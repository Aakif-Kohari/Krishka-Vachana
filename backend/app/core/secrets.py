"""Access to secrets held in Google Secret Manager."""

import logging
from functools import lru_cache

from fastapi import Depends, status

from app.core.config import Settings, get_settings
from app.core.exceptions import AppError

logger = logging.getLogger("app.secrets")


@lru_cache
def _access_secret(resource_name: str) -> bytes:
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(request={"name": resource_name})
    return response.payload.data


def get_aadhaar_hmac_key(settings: Settings = Depends(get_settings)) -> bytes:
    """Retrieve the key used for Aadhaar fingerprints, failing closed."""
    if not settings.aadhaar_hmac_secret_name:
        raise AppError(
            "Aadhaar registration is temporarily unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="service_unavailable",
        )

    try:
        key = _access_secret(settings.aadhaar_hmac_secret_name)
    except Exception as exc:  # pragma: no cover - depends on live infra
        logger.exception("Failed to retrieve the Aadhaar HMAC key")
        raise AppError(
            "Aadhaar registration is temporarily unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="service_unavailable",
        ) from exc

    if len(key) < 32:
        raise AppError(
            "Aadhaar registration is temporarily unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="service_unavailable",
        )
    return key
