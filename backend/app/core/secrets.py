"""Access to secrets held in Google Secret Manager."""

import logging
import re
from functools import lru_cache

from fastapi import Depends, status

from app.core.config import Settings, get_settings
from app.core.exceptions import AppError

logger = logging.getLogger("app.secrets")

# Secret Manager resource names look like:
#   projects/{project}/secrets/{secret}/versions/{version}
# {version} must be a pinned numeric version, never a mutable alias like
# "latest". Why this matters, and what it does and doesn't fix:
#
# The Aadhaar fingerprint (farmer_service.py) is HMAC(aadhaar, this key).
# If this resource name pointed at "latest" and Secret Manager rotated the
# secret underneath the app, every fingerprint computed after that moment
# would silently stop matching fingerprints computed before it - with no
# error, log, or signal. Aadhaar uniqueness enforcement (get_by_aadhaar_hash
# / reserve_aadhaar) would silently start allowing duplicate real-world
# Aadhaar numbers to register under different farmer_ids. Pinning to an
# explicit version turns that into a deliberate, visible config change
# (edit this env var, redeploy) instead of a silent one.
#
# What pinning does NOT fix: because the app never stores the plaintext
# Aadhaar number (by design), it cannot recompute an existing farmer's
# fingerprint under a new key after the fact. So even a deliberate,
# intentional rotation to a new pinned version means new registrations are
# no longer checked against farmers who registered under the old version -
# duplicate detection for that Aadhaar effectively lapses at rotation.
# Closing that gap fully requires checking candidate fingerprints against
# multiple supported prior key versions during registration (a real
# feature, not a one-line fix) - out of scope for this PR. Until that
# exists, treat this key as effectively permanent: avoid rotating it in
# production, and if you must, know that it comes with this trade-off.
_PINNED_VERSION_RE = re.compile(r"^projects/[^/]+/secrets/[^/]+/versions/\d+$")


def _unavailable() -> AppError:
    """Create a 503 error indicating Aadhaar registration is unavailable."""
    return AppError(
        "Aadhaar registration is temporarily unavailable",
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        error_code="service_unavailable",
    )


@lru_cache
def _access_secret(resource_name: str) -> bytes:
    """Retrieve a secret from Google Secret Manager by resource name."""
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(request={"name": resource_name})
    return response.payload.data


def get_aadhaar_hmac_key(settings: Settings = Depends(get_settings)) -> bytes:
    """Retrieve the key used for Aadhaar fingerprints, failing closed.

    Requires the configured resource name to pin an explicit numeric secret
    version - see the module-level note above for why, and its limits.
    """
    resource_name = settings.aadhaar_hmac_secret_name
    if not resource_name:
        raise _unavailable()

    if not _PINNED_VERSION_RE.match(resource_name):
        logger.error(
            "AADHAAR_HMAC_SECRET_NAME must pin an explicit numeric version "
            "(.../versions/<N>), not an alias like 'latest': %r",
            resource_name,
        )
        raise _unavailable()

    try:
        key = _access_secret(resource_name)
    except Exception as exc:  # pragma: no cover - depends on live infra
        logger.exception("Failed to retrieve the Aadhaar HMAC key")
        raise _unavailable() from exc

    if len(key) < 32:
        logger.error("Aadhaar HMAC key is shorter than the required 32 bytes")
        raise _unavailable()

    return key
