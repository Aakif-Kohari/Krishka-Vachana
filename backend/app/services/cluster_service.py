"""Village Cluster Booking business logic.

Handles bulk slot bookings for groups of farmers from the same village.
Validates village membership and atomically reserves capacity for the
entire group, rolling back all reservations if capacity is insufficient
for even one farmer in the batch.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import List

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationAppError
from app.repositories.base import CentreRepository, FarmerRepository, SlotBookingRepository
from app.schemas.cluster import ClusterBookingCreate, ClusterBookingOut

logger = logging.getLogger("app.services.cluster_service")


def create_cluster_booking(
    cluster_data: ClusterBookingCreate,
    farmer_uid: str,
    farmer_repo: FarmerRepository,
    booking_repo: SlotBookingRepository,
    centre_repo: CentreRepository,
) -> ClusterBookingOut:
    """
    Create atomic bookings for all farmers in a village cluster.

    Parameters:
    	cluster_data (ClusterBookingCreate): Cluster details, including the farmers, village, centre, date, and slot window.
        farmer_uid (str): Authenticated caller creating the cluster booking.
    	farmer_repo (FarmerRepository): Repository used to verify farmer records.
    	booking_repo (SlotBookingRepository): Repository used to reserve the group's slot capacity.
    	centre_repo (CentreRepository): Repository used to verify the booking centre and retrieve its slot capacity.

    Returns:
    	ClusterBookingOut: Details of the created cluster booking and its individual booking IDs.

    Raises:
        ForbiddenError: If the caller is not a member of the cluster or an authorized delegate.
    	NotFoundError: If a farmer or booking centre does not exist.
    	ValidationAppError: If a farmer does not belong to the requested village.
    	ConflictError: If capacity is insufficient for the entire group.
    """
    # 1. Check authorization FIRST to prevent probing farmer existence/villages
    if (
        farmer_uid not in cluster_data.farmer_ids
        and not farmer_repo.is_cluster_delegate_authorized(
            farmer_uid, cluster_data.farmer_ids
        )
    ):
        raise ForbiddenError("Not authorized to book for this farmer cluster")

    # 2. Validate all farmers exist and belong to the claimed village
    for fid in cluster_data.farmer_ids:
        farmer = farmer_repo.get(fid)
        if not farmer:
            raise NotFoundError(f"Farmer {fid} not found")
        if farmer.get("village") != cluster_data.village:
            raise ValidationAppError(f"Farmer {fid} does not belong to village {cluster_data.village}")

    # 3. Verify centre exists
    centre = centre_repo.get(cluster_data.centre_id)
    if not centre:
        raise NotFoundError(f"Centre {cluster_data.centre_id} not found")
    
    capacity = centre.get("capacity_per_slot", 0)

    # 4. Prepare batch data
    # Pass the native `date` object. The Firestore repo handles ISO serialization,
    # and the in-memory repo keeps it as a `date` object to match `slot_service.book_slot`.
    data_list = []
    booking_ids = []
    for fid in cluster_data.farmer_ids:
        bid = str(uuid.uuid4())
        booking_ids.append(bid)
        data_list.append({
            "farmer_id": fid,
            "centre_id": cluster_data.centre_id,
            "slot_date": cluster_data.slot_date,  # Native date object (Fixes Bug 2)
            "slot_window": cluster_data.slot_window,
            "status": "booked",                   # Matches slot_service.book_slot (Fixes Bug 1)
            "created_at": datetime.now(timezone.utc),
        })

    # 5. Atomic Batch Creation
    created_bookings = booking_repo.create_batch_atomic(
        booking_ids=booking_ids,
        capacity=capacity,
        data_list=data_list
    )

    if created_bookings is None:
        raise ConflictError("Insufficient capacity for the entire village cluster")

    # NOTE: cluster_id is ephemeral and not persisted as a distinct document.
    # In a production system, this would be backed by a dedicated ClusterBooking record.
    return ClusterBookingOut(
        cluster_id=str(uuid.uuid4()),
        village=cluster_data.village,
        booking_ids=booking_ids,
        created_at=datetime.now(timezone.utc),
    )
