"""Tests for the generic SMS gateway client (app/core/sms.py)."""
import logging

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.core.sms import send_sms


def test_send_sms_dry_run_when_unconfigured(caplog):
    """Test that SMS sending logs and returns False when gateway is not configured."""
    settings = Settings(sms_gateway_base_url="")
    with caplog.at_level(logging.INFO, logger="app.sms"):
        sent = send_sms(settings, "9876543210", "hello")
    assert sent is False
    assert "gateway not configured" in caplog.text
    assert "9876543210" not in caplog.text
    assert "hello" not in caplog.text


def test_send_sms_posts_when_configured(monkeypatch):
    """Test that SMS sends properly formatted POST request when gateway is configured."""
    settings = Settings(sms_gateway_base_url="https://sms.example.com/send", sms_gateway_api_key="secret-key")
    captured = {}

    class _FakeResponse:
        """Mock HTTP response for testing."""
        def raise_for_status(self):
            """Mock method to simulate HTTP status checks."""
            return None

    def fake_post(url, json, headers, timeout):
        """Mock POST request that captures arguments."""
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout
        return _FakeResponse()

    monkeypatch.setattr("app.core.sms.httpx.post", fake_post)

    sent = send_sms(settings, "9876543210", "hello")

    assert sent is True
    assert captured["url"] == "https://sms.example.com/send"
    assert captured["json"] == {"to": "9876543210", "message": "hello"}
    assert captured["headers"]["Authorization"] == "Bearer secret-key"


def test_send_sms_handles_gateway_failure(monkeypatch, caplog):
    """Test that SMS gateway failures are logged and return False without raising."""
    settings = Settings(sms_gateway_base_url="https://sms.example.com/send")

    def fake_post(*args, **kwargs):
        """Mock POST that raises connection error."""
        raise ConnectionError("gateway unreachable")

    monkeypatch.setattr("app.core.sms.httpx.post", fake_post)

    with caplog.at_level(logging.ERROR, logger="app.sms"):
        sent = send_sms(settings, "9876543210", "hello")

    assert sent is False
    assert "Failed to send SMS" in caplog.text


def test_send_sms_omits_auth_header_without_api_key(monkeypatch):
    """Test that Authorization header is omitted when no API key is configured."""
    settings = Settings(sms_gateway_base_url="https://sms.example.com/send", sms_gateway_api_key="")
    captured = {}

    class _FakeResponse:
        """Mock HTTP response for testing."""
        def raise_for_status(self):
            """Mock method to simulate HTTP status checks."""
            return None

    def fake_post(url, json, headers, timeout):
        """Mock POST request that captures headers."""
        captured["headers"] = headers
        return _FakeResponse()

    monkeypatch.setattr("app.core.sms.httpx.post", fake_post)

    send_sms(settings, "9876543210", "hello")

    assert "Authorization" not in captured["headers"]


@pytest.mark.parametrize("timeout", [0, -1.0])
def test_sms_gateway_timeout_rejects_non_positive_values(timeout):
    """Test that only positive timeout values are accepted when configured."""
    with pytest.raises(ValidationError):
        Settings(sms_gateway_timeout_seconds=timeout)


def test_sms_gateway_timeout_allows_none_to_disable_httpx_timeout(monkeypatch):
    """Test that None remains the explicit way to disable the HTTPX timeout."""
    settings = Settings(
        sms_gateway_base_url="https://sms.example.com/send",
        sms_gateway_timeout_seconds=None,
    )
    captured = {}

    class _FakeResponse:
        def raise_for_status(self):
            """Mock method to simulate HTTP status checks."""
            return None

    def fake_post(*_args, **kwargs):
        """Mock POST request to capture timeout parameter."""
        captured["timeout"] = kwargs["timeout"]
        return _FakeResponse()

    monkeypatch.setattr("app.core.sms.httpx.post", fake_post)

    assert send_sms(settings, "9876543210", "hello") is True
    assert captured["timeout"] is None
