def test_liveness_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "kisansetu-backend"
    assert "version" in body
    assert "uptime_seconds" in body


def test_readiness_check_without_firebase_configured(client):
    # In tests, Firebase isn't configured, so readiness should report the
    # in-memory fallback as healthy rather than failing.
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "not_configured" in body["checks"]["firestore"]


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "KisanSetu API"
    assert body["health"] == "/api/v1/health"
