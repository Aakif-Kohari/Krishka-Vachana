from datetime import date, timedelta

TOMORROW = (date.today() + timedelta(days=1)).isoformat()


def test_list_centres_returns_seed_data(client, auth_headers):
    """Verify that listing centres returns seeded data."""
    response = client.get("/api/v1/centres", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) >= 1
    assert {"centre_id", "name", "district", "state", "capacity_per_slot"} <= body[0].keys()


def test_list_centres_filters_by_district(client, auth_headers, centre_repo):
    """Verify that centres can be filtered by district."""
    target_district = centre_repo.list()[0]["district"]
    response = client.get(f"/api/v1/centres?district={target_district}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) >= 1
    assert all(c["district"] == target_district for c in body)


def test_list_centres_filter_is_case_insensitive(client, auth_headers, centre_repo):
    """Verify that district filtering is case-insensitive."""
    target_district = centre_repo.list()[0]["district"]
    response = client.get(f"/api/v1/centres?district={target_district.upper()}", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_list_centres_unknown_district_returns_empty(client, auth_headers):
    """Verify that filtering by an unknown district returns an empty list."""
    response = client.get("/api/v1/centres?district=NoSuchDistrict", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_centre_success(client, auth_headers, seeded_centre_id):
    """Verify that a centre can be retrieved by ID."""
    response = client.get(f"/api/v1/centres/{seeded_centre_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["centre_id"] == seeded_centre_id


def test_get_centre_not_found(client, auth_headers):
    """Verify that fetching a non-existent centre returns 404."""
    response = client.get("/api/v1/centres/does-not-exist", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_get_centre_congestion_defaults_to_low_when_no_bookings(client, auth_headers, seeded_centre_id):
    """Verify that congestion defaults to low when no bookings exist."""
    response = client.get(
        f"/api/v1/centres/{seeded_centre_id}/congestion?slot_date={TOMORROW}", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "heuristic_fallback"
    assert len(body["windows"]) == 6
    assert all(w["booked_count"] == 0 for w in body["windows"])
    assert all(w["congestion_level"] == "low" for w in body["windows"])
    assert body["alternative_centres"] == []


def test_get_centre_congestion_unknown_centre_is_404(client, auth_headers):
    """Verify that fetching congestion for an unknown centre returns 404."""
    response = client.get(f"/api/v1/centres/does-not-exist/congestion?slot_date={TOMORROW}", headers=auth_headers)
    assert response.status_code == 404


def test_get_centre_congestion_requires_date_param(client, auth_headers, seeded_centre_id):
    """Verify that the congestion endpoint requires a date parameter."""
    response = client.get(f"/api/v1/centres/{seeded_centre_id}/congestion", headers=auth_headers)
    assert response.status_code == 422


def test_get_centre_congestion_reflects_real_bookings(client, auth_headers, seeded_centre_id):
    """Verify that congestion predictions reflect actual bookings."""
    client.post(
        "/api/v1/farmers/register",
        json={
            "full_name": "Ravi Kumar",
            "phone_number": "9876543210",
            "aadhaar_number": "123456789012",
            "village": "Rajpur",
            "district": "Solapur",
            "state": "Maharashtra",
            "preferred_language": "mr",
        },
        headers=auth_headers,
    )
    client.post(
        "/api/v1/bookings",
        json={"centre_id": seeded_centre_id, "slot_date": TOMORROW, "slot_window": "08:00-10:00"},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/centres/{seeded_centre_id}/congestion?slot_date={TOMORROW}", headers=auth_headers
    )
    assert response.status_code == 200
    windows = {w["slot_window"]: w for w in response.json()["windows"]}
    assert windows["08:00-10:00"]["booked_count"] == 1
    assert windows["06:00-08:00"]["booked_count"] == 0
