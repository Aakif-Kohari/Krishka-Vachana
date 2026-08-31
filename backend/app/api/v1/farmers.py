from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_farmer_uid, get_farmer_repository
from app.core.secrets import get_aadhaar_hmac_key
from app.repositories.base import FarmerRepository
from app.schemas.farmer import FarmerCreate, FarmerOut, FarmerUpdate
from app.services import farmer_service

router = APIRouter(prefix="/farmers", tags=["farmers"])


@router.post("/register", response_model=FarmerOut, status_code=status.HTTP_201_CREATED)
def register_farmer(
    payload: FarmerCreate,
    farmer_id: str = Depends(get_current_farmer_uid),
    repo: FarmerRepository = Depends(get_farmer_repository),
    aadhaar_hmac_key: bytes = Depends(get_aadhaar_hmac_key),
) -> FarmerOut:
    return farmer_service.register_farmer(repo, farmer_id, payload, aadhaar_hmac_key)


@router.get("/me", response_model=FarmerOut)
def get_my_profile(
    farmer_id: str = Depends(get_current_farmer_uid),
    repo: FarmerRepository = Depends(get_farmer_repository),
) -> FarmerOut:
    return farmer_service.get_farmer_profile(repo, farmer_id)


@router.patch("/me", response_model=FarmerOut)
def update_my_profile(
    payload: FarmerUpdate,
    farmer_id: str = Depends(get_current_farmer_uid),
    repo: FarmerRepository = Depends(get_farmer_repository),
) -> FarmerOut:
    return farmer_service.update_farmer_profile(repo, farmer_id, payload)
