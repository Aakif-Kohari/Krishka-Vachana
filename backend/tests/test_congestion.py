from datetime import date, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.repositories.memory import InMemoryCentreRepository, InMemorySlotBookingRepository
from app.services import congestion_service

TOMORROW = date.today() + timedelta(days=1)


def _repos(capacity: int = 2):
    seed = [
        {
            "centre_id": "ctr-a",
            "name": "Centre A",
            "village": "A",
            "district": "Solapur",
            "state": "Maharashtra",
            "capacity_per_slot": capacity,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "centre_id": "ctr-b",
            "name": "Centre B",
            "village": "B",
            "district": "Solapur",
            "state": "Maharashtra",
            "capacity_per_slot": capacity,
            "created_at": datetime.now(timezone.utc),
        },
    ]
    return InMemoryCentreRepository(seed=seed), InMemorySlotBookingRepository()


def _book(booking_repo, booking_id, centre_id, capacity, window, farmer_id):
    return booking_repo.create_if_capacity_available(
        booking_id,
        capacity,
        {
            "farmer_id": farmer_id,
            "centre_id": centre_id,
            "slot_date": TOMORROW,
            "slot_window": window,
            "crop_id": None,
            "notes": None,
            "status": "booked",
            "created_at": datetime.now(timezone.utc),
        },
    )


def test_falls_back_to_heuristic_when_no_ml_endpoint_configured():
    centre_repo, booking_repo = _repos()
    settings = Settings(congestion_prediction_api_url="")

    result = congestion_service.predict_congestion(settings, centre_repo, booking_repo, "ctr-a", TOMORROW)

    assert result.source == "heuristic_fallback"
    assert len(result.windows) == 6
    assert all(w.booked_count == 0 for w in result.windows)
    assert all(w.congestion_level == "low" for w in result.windows)
    assert result.alternative_centres == []


def test_unknown_centre_raises_not_found():
    centre_repo, booking_repo = _repos()
    settings = Settings(congestion_prediction_api_url="")

    with pytest.raises(NotFoundError):
        congestion_service.predict_congestion(settings, centre_repo, booking_repo, "does-not-exist", TOMORROW)


def test_heuristic_reflects_actual_bookings():
    centre_repo, booking_repo = _repos(capacity=2)
    _book(booking_repo, "b1", "ctr-a", 2, "08:00-10:00", "f1")
    _book(booking_repo, "b2", "ctr-a", 2, "08:00-10:00", "f2")
    settings = Settings(congestion_prediction_api_url="")

    result = congestion_service.predict_congestion(settings, centre_repo, booking_repo, "ctr-a", TOMORROW)

    window = next(w for w in result.windows if w.slot_window == "08:00-10:00")
    assert window.booked_count == 2
    assert window.congestion_level == "high"  # 2/2 capacity


def test_suggests_alternative_centre_when_busy():
    centre_repo, booking_repo = _repos(capacity=2)
    _book(booking_repo, "b1", "ctr-a", 2, "08:00-10:00", "f1")
    _book(booking_repo, "b2", "ctr-a", 2, "08:00-10:00", "f2")
    settings = Settings(congestion_prediction_api_url="")

    result = congestion_service.predict_congestion(settings, centre_repo, booking_repo, "ctr-a", TOMORROW)

    assert any(a.centre_id == "ctr-b" for a in result.alternative_centres)


def test_no_alternatives_suggested_when_everything_is_quiet():
    centre_repo, booking_repo = _repos()
    settings = Settings(congestion_prediction_api_url="")

    result = congestion_service.predict_congestion(settings, centre_repo, booking_repo, "ctr-a", TOMORROW)

    assert result.alternative_centres == []


def test_uses_ml_endpoint_when_configured(monkeypatch):
    centre_repo, booking_repo = _repos()
    settings = Settings(congestion_prediction_api_url="https://ml.example.com/predict")

    class _FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "windows": [
                    {
                        "slot_window": w,
                        "booked_count": 0,
                        "capacity_per_slot": 2,
                        "congestion_level": "low",
                    }
                    for w in [
                        "06:00-08:00",
                        "08:00-10:00",
                        "10:00-12:00",
                        "12:00-14:00",
                        "14:00-16:00",
                        "16:00-18:00",
                    ]
                ],
                "alternative_centres": [],
            }

    def _fake_post(url, json, timeout):
        assert url == "https://ml.example.com/predict"
        assert json["centre_id"] == "ctr-a"
        return _FakeResponse()

    monkeypatch.setattr("app.services.congestion_service.httpx.post", _fake_post)

    result = congestion_service.predict_congestion(settings, centre_repo, booking_repo, "ctr-a", TOMORROW)

    assert result.source == "ml_model"


def test_falls_back_to_heuristic_when_ml_endpoint_errors(monkeypatch, caplog):
    centre_repo, booking_repo = _repos()
    settings = Settings(congestion_prediction_api_url="https://ml.example.com/predict")

    def _fake_post(*args, **kwargs):
        raise RuntimeError("ML service unreachable")

    monkeypatch.setattr("app.services.congestion_service.httpx.post", _fake_post)

    result = congestion_service.predict_congestion(settings, centre_repo, booking_repo, "ctr-a", TOMORROW)

    assert result.source == "heuristic_fallback"


def test_congestion_schema_rejects_unknown_level():
    from app.schemas.congestion import SlotWindowCongestion

    with pytest.raises(ValidationError):
        SlotWindowCongestion(
            slot_window="08:00-10:00",
            booked_count=0,
            capacity_per_slot=2,
            congestion_level="unknown",
        )
