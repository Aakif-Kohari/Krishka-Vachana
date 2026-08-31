"""Farmer registration & profile business logic."""
import hashlib
import hmac

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.base import FarmerRepository
from app.schemas.farmer import FarmerCreate, FarmerOut, FarmerUpdate, utcnow


_FINGERPRINT_VERSION = "hmac-sha256:v1"


def _normalize_aadhaar(aadhaar_number: str) -> str:
    return aadhaar_number.strip()


def _fingerprint_aadhaar(aadhaar_number: str, key: bytes) -> str:
    """Keyed, one-way fingerprint of the normalized Aadhaar number.

    We never persist the plaintext number - only this fingerprint (for
    dedupe/verification needs) and the last 4 digits (for display,
    matching common Indian e-KYC UX of showing "XXXX-XXXX-1234").
    """
    normalized = _normalize_aadhaar(aadhaar_number).encode("utf-8")
    digest = hmac.new(key, normalized, hashlib.sha256).hexdigest()
    return f"{_FINGERPRINT_VERSION}:{digest}"


def _legacy_aadhaar_hash(aadhaar_number: str) -> str:
    normalized = _normalize_aadhaar(aadhaar_number).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def register_farmer(
    repo: FarmerRepository,
    farmer_id: str,
    payload: FarmerCreate,
    aadhaar_hmac_key: bytes,
) -> FarmerOut:
    existing = repo.get(farmer_id)
    if existing is not None:
        raise ConflictError("Farmer profile already exists for this account")

    aadhaar_fingerprint = _fingerprint_aadhaar(payload.aadhaar_number, aadhaar_hmac_key)
    # Existing records used an unkeyed SHA-256 hash. Reserve the new
    # fingerprint for that record before migrating it so the migration cannot
    # introduce the same fingerprint as a concurrent registration.
    duplicate = repo.get_by_aadhaar_hash(_legacy_aadhaar_hash(payload.aadhaar_number))
    reservation_owner = duplicate["farmer_id"] if duplicate is not None else farmer_id
    if not repo.reserve_aadhaar(aadhaar_fingerprint, reservation_owner):
        raise ConflictError("A farmer profile already exists for this Aadhaar number")
    if duplicate is not None:
        repo.update(duplicate["farmer_id"], {"aadhaar_hash": aadhaar_fingerprint})
        raise ConflictError("A farmer profile already exists for this Aadhaar number")

    record = repo.create(
        farmer_id,
        {
            "full_name": payload.full_name,
            "phone_number": payload.phone_number,
            "aadhaar_hash": aadhaar_fingerprint,
            "aadhaar_last4": payload.aadhaar_number[-4:],
            "village": payload.village,
            "district": payload.district,
            "state": payload.state,
            "preferred_language": payload.preferred_language,
            "created_at": utcnow(),
        },
    )
    return FarmerOut.model_validate(record)


def get_farmer_profile(repo: FarmerRepository, farmer_id: str) -> FarmerOut:
    record = repo.get(farmer_id)
    if record is None:
        raise NotFoundError("Farmer profile not found - register first")
    return FarmerOut.model_validate(record)


def update_farmer_profile(repo: FarmerRepository, farmer_id: str, payload: FarmerUpdate) -> FarmerOut:
    if repo.get(farmer_id) is None:
        raise NotFoundError("Farmer profile not found - register first")

    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    record = repo.update(farmer_id, updates)
    return FarmerOut.model_validate(record)
