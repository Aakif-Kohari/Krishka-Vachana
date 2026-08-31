"""Farmer registration & profile business logic."""
import hashlib

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.base import FarmerRepository
from app.schemas.farmer import FarmerCreate, FarmerOut, FarmerUpdate, utcnow


def _hash_aadhaar(aadhaar_number: str) -> str:
    """One-way hash of the full Aadhaar number.

    We never persist the plaintext number - only this hash (for potential
    future dedupe/verification needs) and the last 4 digits (for display,
    matching common Indian e-KYC UX of showing "XXXX-XXXX-1234").
    """
    return hashlib.sha256(aadhaar_number.encode("utf-8")).hexdigest()


def register_farmer(repo: FarmerRepository, farmer_id: str, payload: FarmerCreate) -> FarmerOut:
    existing = repo.get(farmer_id)
    if existing is not None:
        raise ConflictError("Farmer profile already exists for this account")

    record = repo.create(
        farmer_id,
        {
            "full_name": payload.full_name,
            "phone_number": payload.phone_number,
            "aadhaar_hash": _hash_aadhaar(payload.aadhaar_number),
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
