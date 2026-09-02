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
from typing import List

from pydantic import BaseModel, Field

CONGESTION_LEVELS = ["low", "moderate", "high"]


class SlotWindowCongestion(BaseModel):
    slot_window: str
    booked_count: int
    capacity_per_slot: int
    congestion_level: str = Field(description=f"One of {CONGESTION_LEVELS}")


class AlternativeCentre(BaseModel):
    centre_id: str
    name: str
    district: str
    congestion_level: str


class CongestionOut(BaseModel):
    centre_id: str
    date: date_type
    source: str = Field(
        description="'ml_model' once AI/ML's endpoint is wired in, otherwise 'heuristic_fallback'"
    )
    windows: List[SlotWindowCongestion]
    alternative_centres: List[AlternativeCentre] = Field(default_factory=list)
