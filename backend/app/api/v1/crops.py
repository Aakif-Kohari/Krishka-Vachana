from typing import List

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_farmer_uid, get_crop_repository, get_farmer_repository
from app.repositories.base import CropRepository, FarmerRepository
from app.schemas.crop import CropOut, CropRegistrationCreate
from app.services import crop_service

router = APIRouter(prefix="/crops", tags=["crops"])


@router.post("", response_model=CropOut, status_code=status.HTTP_201_CREATED)
def register_crop(
    payload: CropRegistrationCreate,
    farmer_id: str = Depends(get_current_farmer_uid),
    crop_repo: CropRepository = Depends(get_crop_repository),
    farmer_repo: FarmerRepository = Depends(get_farmer_repository),
) -> CropOut:
    """Register a crop and quantity for the authenticated farmer."""
    return crop_service.register_crop(crop_repo, farmer_repo, farmer_id, payload)


@router.get("/me", response_model=List[CropOut])
def list_my_crops(
    farmer_id: str = Depends(get_current_farmer_uid),
    crop_repo: CropRepository = Depends(get_crop_repository),
) -> List[CropOut]:
    """List all crops registered by the authenticated farmer."""
    return crop_service.list_crops_for_farmer(crop_repo, farmer_id)
