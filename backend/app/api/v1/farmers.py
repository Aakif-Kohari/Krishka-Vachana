from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_farmer_uid, get_farmer_repository
from app.core.config import Settings, get_settings
from app.core.secrets import get_aadhaar_hmac_key
from app.repositories.base import FarmerRepository
from app.schemas.farmer import FarmerCreate, FarmerOut, FarmerUpdate
from app.schemas.otp import OtpRequestOut, OtpVerifyOut, OtpVerifyRequest
from app.services import farmer_service, otp_service

router = APIRouter(prefix="/farmers", tags=["farmers"])


@router.post("/register", response_model=FarmerOut, status_code=status.HTTP_201_CREATED)
def register_farmer(
    payload: FarmerCreate,
    farmer_id: str = Depends(get_current_farmer_uid),
    repo: FarmerRepository = Depends(get_farmer_repository),
    aadhaar_hmac_key: bytes = Depends(get_aadhaar_hmac_key),
) -> FarmerOut:
    """Register a new farmer profile with Aadhaar-linked identification."""
    return farmer_service.register_farmer(repo, farmer_id, payload, aadhaar_hmac_key)


@router.get("/me", response_model=FarmerOut)
def get_my_profile(
    farmer_id: str = Depends(get_current_farmer_uid),
    repo: FarmerRepository = Depends(get_farmer_repository),
) -> FarmerOut:
    """Get the authenticated farmer's profile."""
    return farmer_service.get_farmer_profile(repo, farmer_id)


@router.patch("/me", response_model=FarmerOut)
def update_my_profile(
    payload: FarmerUpdate,
    farmer_id: str = Depends(get_current_farmer_uid),
    repo: FarmerRepository = Depends(get_farmer_repository),
) -> FarmerOut:
    """Update the authenticated farmer's profile."""
    return farmer_service.update_farmer_profile(repo, farmer_id, payload)


@router.post("/me/phone/otp/request", response_model=OtpRequestOut)
def request_phone_otp(
    farmer_id: str = Depends(get_current_farmer_uid),
    repo: FarmerRepository = Depends(get_farmer_repository),
    settings: Settings = Depends(get_settings),
) -> OtpRequestOut:
    """Send a one-time verification code to the authenticated farmer's registered phone number."""
    return otp_service.request_otp(settings, repo, farmer_id)


@router.post("/me/phone/otp/verify", response_model=OtpVerifyOut)
def verify_phone_otp(
    payload: OtpVerifyRequest,
    farmer_id: str = Depends(get_current_farmer_uid),
    repo: FarmerRepository = Depends(get_farmer_repository),
    settings: Settings = Depends(get_settings),
) -> OtpVerifyOut:
    """Verify a submitted OTP code and mark the farmer's phone number as verified."""
    return otp_service.verify_otp(settings, repo, farmer_id, payload.otp_code)
