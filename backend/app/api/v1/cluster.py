"""Village Cluster Booking API endpoints."""
from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_centre_repository,
    get_current_farmer_uid,
    get_farmer_repository,
    get_slot_booking_repository,
)
from app.repositories.base import CentreRepository, FarmerRepository, SlotBookingRepository
from app.schemas.cluster import ClusterBookingCreate, ClusterBookingOut
from app.services import cluster_service

router = APIRouter(prefix="/bookings", tags=["cluster"])


@router.post("/cluster", response_model=ClusterBookingOut, status_code=status.HTTP_201_CREATED)
def create_cluster_booking_endpoint(
    cluster_data: ClusterBookingCreate,
    farmer_uid: str = Depends(get_current_farmer_uid),
    farmer_repo: FarmerRepository = Depends(get_farmer_repository),
    booking_repo: SlotBookingRepository = Depends(get_slot_booking_repository),
    centre_repo: CentreRepository = Depends(get_centre_repository),
) -> ClusterBookingOut:
    """Book a Smart Slot for a cluster of farmers from the same village."""
    return cluster_service.create_cluster_booking(cluster_data, farmer_repo, booking_repo, centre_repo)
