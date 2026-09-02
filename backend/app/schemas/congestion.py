"""Congestion-prediction integration-point schemas.

This is the *integration point* the backend README roadmap promises for
Phase 2: a stable request/response contract, backed by a working endpoint
today (a simple occupancy heuristic - see
app/services/congestion_service.py), that AI/ML can drop their real model
behind later by standing up CONGESTION_PREDICTION_API_URL
(app/core/config.py) with the same response shape. No route or schema
changes are needed on either side when that happens.
"""
from datetime import date as date_type
from typing import List, Literal

from pydantic import BaseModel, Field

CONGESTION_LEVELS = ["low", "moderate", "high"]
CongestionLevel = Literal["low", "moderate", "high"]


class CongestionPredictionRequest(BaseModel):
    """Request payload sent to AI/ML's congestion-prediction endpoint.

    Typed (rather than a raw dict) so the integration contract in this
    module's docstring can't silently drift from what
    app/services/congestion_service.py actually sends.
    """

    centre_id: str
    date: date_type
    capacity_per_slot: int = Field(gt=0)
    slot_windows: List[str]


class SlotWindowCongestion(BaseModel):
    """Congestion information for a single slot window."""

    slot_window: str
    booked_count: int = Field(ge=0)
    capacity_per_slot: int = Field(gt=0)
    congestion_level: CongestionLevel = Field(description=f"One of {CONGESTION_LEVELS}")


class AlternativeCentre(BaseModel):
    """Alternative procurement centre suggestion with lower congestion."""

    centre_id: str
    name: str
    district: str
    congestion_level: CongestionLevel


class CongestionOut(BaseModel):
    """Congestion prediction response for a centre on a specific date."""

    centre_id: str
    date: date_type
    source: str = Field(
        description="'ml_model' once AI/ML's endpoint is wired in, otherwise 'heuristic_fallback'"
    )
    windows: List[SlotWindowCongestion]
    alternative_centres: List[AlternativeCentre] = Field(default_factory=list)
