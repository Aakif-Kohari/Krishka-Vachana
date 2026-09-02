"""Congestion-prediction integration point.

Phase 2 backend scope (see README roadmap) is delivering the *integration
point* itself: a stable endpoint/contract that AI/ML's real model will sit
behind, not the model itself (that's the AI/ML role's job per
team_work_division.md - "expose model predictions via an API endpoint
...works closely with Backend Developer to integrate into FastAPI").
Until AI/ML's endpoint exists, or if it's temporarily unreachable, this
degrades to a deterministic heuristic based on today's actual
booked/capacity ratio per slot window - the same graceful-fallback shape
app/core/firebase.py already uses for Firestore.
"""
import logging
from datetime import date as date_type
from typing import Dict, List

import httpx

from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.repositories.base import CentreRepository, SlotBookingRepository
from app.schemas.centre import SLOT_WINDOWS
from app.schemas.congestion import AlternativeCentre, CongestionOut, SlotWindowCongestion

logger = logging.getLogger("app.congestion")

# Ratio of booked/capacity at or above which a window is considered
# moderately/highly congested. Simple fixed thresholds for the Phase 2
# heuristic - AI/ML's real model can use whatever signal it wants once
# CONGESTION_PREDICTION_API_URL is configured.
_MODERATE_THRESHOLD = 0.5
_HIGH_THRESHOLD = 0.85

_LEVEL_ORDER = ["low", "moderate", "high"]


def _level_for_ratio(ratio: float) -> str:
    if ratio >= _HIGH_THRESHOLD:
        return "high"
    if ratio >= _MODERATE_THRESHOLD:
        return "moderate"
    return "low"


def _heuristic_windows(
    booking_repo: SlotBookingRepository, centre_id: str, slot_date: date_type, capacity: int
) -> List[SlotWindowCongestion]:
    windows = []
    for window in SLOT_WINDOWS:
        booked = booking_repo.count_active_bookings(centre_id, slot_date, window)
        ratio = booked / capacity if capacity else 1.0
        windows.append(
            SlotWindowCongestion(
                slot_window=window,
                booked_count=booked,
                capacity_per_slot=capacity,
                congestion_level=_level_for_ratio(ratio),
            )
        )
    return windows


def _alternative_centres(
    centre_repo: CentreRepository,
    booking_repo: SlotBookingRepository,
    centre: Dict,
    slot_date: date_type,
    windows: List[SlotWindowCongestion],
) -> List[AlternativeCentre]:
    # Only bother suggesting alternatives if this centre isn't already
    # comfortably low-congestion across the whole day.
    if all(w.congestion_level == "low" for w in windows):
        return []

    alternatives: List[AlternativeCentre] = []
    for candidate in centre_repo.list(district=centre["district"]):
        if candidate["centre_id"] == centre["centre_id"]:
            continue
        candidate_windows = _heuristic_windows(
            booking_repo, candidate["centre_id"], slot_date, candidate["capacity_per_slot"]
        )
        best_window = min(candidate_windows, key=lambda w: _LEVEL_ORDER.index(w.congestion_level))
        if best_window.congestion_level == "low":
            alternatives.append(
                AlternativeCentre(
                    centre_id=candidate["centre_id"],
                    name=candidate["name"],
                    district=candidate["district"],
                    congestion_level=best_window.congestion_level,
                )
            )
    return alternatives[:3]


def predict_congestion(
    settings: Settings,
    centre_repo: CentreRepository,
    booking_repo: SlotBookingRepository,
    centre_id: str,
    slot_date: date_type,
) -> CongestionOut:
    centre = centre_repo.get(centre_id)
    if centre is None:
        raise NotFoundError("Procurement centre not found")

    if settings.congestion_prediction_api_url:
        try:
            response = httpx.post(
                settings.congestion_prediction_api_url,
                json={
                    "centre_id": centre_id,
                    "date": slot_date.isoformat(),
                    "capacity_per_slot": centre["capacity_per_slot"],
                    "slot_windows": SLOT_WINDOWS,
                },
                timeout=settings.congestion_prediction_api_timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            return CongestionOut(
                centre_id=centre_id,
                date=slot_date,
                source="ml_model",
                windows=[SlotWindowCongestion(**w) for w in payload["windows"]],
                alternative_centres=[
                    AlternativeCentre(**a) for a in payload.get("alternative_centres", [])
                ],
            )
        except Exception:  # pragma: no cover - depends on live AI/ML service
            logger.exception(
                "Congestion-prediction API call failed; falling back to the occupancy heuristic"
            )

    windows = _heuristic_windows(booking_repo, centre_id, slot_date, centre["capacity_per_slot"])
    alternatives = _alternative_centres(centre_repo, booking_repo, centre, slot_date, windows)
    return CongestionOut(
        centre_id=centre_id,
        date=slot_date,
        source="heuristic_fallback",
        windows=windows,
        alternative_centres=alternatives,
    )
