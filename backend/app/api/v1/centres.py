from datetime import date as date_type
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_centre_repository, get_current_farmer_uid, get_slot_booking_repository
from app.core.config import Settings, get_settings
from app.repositories.base import CentreRepository, SlotBookingRepository
from app.schemas.centre import CentreOut
from app.schemas.congestion import CongestionOut
from app.services import centre_service, congestion_service

router = APIRouter(prefix="/centres", tags=["centres"])


@router.get("", response_model=List[CentreOut])
def list_centres(
    district: Optional[str] = Query(default=None, description="Filter by district"),
    state: Optional[str] = Query(default=None, description="Filter by state"),
    farmer_id: str = Depends(get_current_farmer_uid),
    repo: CentreRepository = Depends(get_centre_repository),
) -> List[CentreOut]:
    return centre_service.list_centres(repo, district=district, state=state)


@router.get("/{centre_id}", response_model=CentreOut)
def get_centre(
    centre_id: str,
    farmer_id: str = Depends(get_current_farmer_uid),
    repo: CentreRepository = Depends(get_centre_repository),
) -> CentreOut:
    return centre_service.get_centre(repo, centre_id)


@router.get("/{centre_id}/congestion", response_model=CongestionOut)
def get_centre_congestion(
    centre_id: str,
    slot_date: date_type = Query(description="Date to predict congestion for (YYYY-MM-DD)"),
    farmer_id: str = Depends(get_current_farmer_uid),
    settings: Settings = Depends(get_settings),
    centre_repo: CentreRepository = Depends(get_centre_repository),
    booking_repo: SlotBookingRepository = Depends(get_slot_booking_repository),
) -> CongestionOut:
    return congestion_service.predict_congestion(settings, centre_repo, booking_repo, centre_id, slot_date)
