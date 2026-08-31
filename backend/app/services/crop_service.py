"""Crop & quantity registration business logic."""
import uuid
from typing import List

from app.repositories.base import CropRepository, FarmerRepository
from app.core.exceptions import NotFoundError
from app.schemas.crop import CropOut, CropRegistrationCreate, utcnow


def register_crop(
    crop_repo: CropRepository,
    farmer_repo: FarmerRepository,
    farmer_id: str,
    payload: CropRegistrationCreate,
) -> CropOut:
    if farmer_repo.get(farmer_id) is None:
        raise NotFoundError("Register a farmer profile before registering crops")

    crop_id = str(uuid.uuid4())
    record = crop_repo.create(
        crop_id,
        {
            "farmer_id": farmer_id,
            "crop_type": payload.crop_type,
            "crop_type_other": payload.crop_type_other,
            "quantity_quintals": payload.quantity_quintals,
            "notes": payload.notes,
            "created_at": utcnow(),
        },
    )
    return CropOut.model_validate(record)


def list_crops_for_farmer(crop_repo: CropRepository, farmer_id: str) -> List[CropOut]:
    records = crop_repo.list_by_farmer(farmer_id)
    records.sort(key=lambda r: r["created_at"], reverse=True)
    return [CropOut.model_validate(r) for r in records]
