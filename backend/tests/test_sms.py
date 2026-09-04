"""Tests for the generic SMS gateway client (app/core/sms.py)."""
import logging

from app.core.config import Settings
from app.core.sms import send_sms


def test_send_sms_dry_run_when_unconfigured(caplog):
    settings = Settings(sms_gateway_base_url="")
    with caplog.at_level(logging.INFO, logger="app.sms"):
        sent = send_sms(settings, "9876543210", "hello")
    assert sent is False
    assert "dry run" in caplog.text
    assert "9876543210" in caplog.text


def test_send_sms_posts_when_configured(monkeypatch):
    settings = Settings(sms_gateway_base_url="https://sms.example.com/send", sms_gateway_api_key="secret-key")
    captured = {}

    class _FakeResponse:
        def raise_for_status(self):
            return None

    def fake_post(url, json, headers, timeout):
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
    settings = Settings(sms_gateway_base_url="https://sms.example.com/send")

    def fake_post(*args, **kwargs):
        raise ConnectionError("gateway unreachable")

    monkeypatch.setattr("app.core.sms.httpx.post", fake_post)

    with caplog.at_level(logging.ERROR, logger="app.sms"):
        sent = send_sms(settings, "9876543210", "hello")

    assert sent is False
    assert "Failed to send SMS" in caplog.text


def test_send_sms_omits_auth_header_without_api_key(monkeypatch):
    settings = Settings(sms_gateway_base_url="https://sms.example.com/send", sms_gateway_api_key="")
    captured = {}

    class _FakeResponse:
        def raise_for_status(self):
            return None

    def fake_post(url, json, headers, timeout):
        captured["headers"] = headers
        return _FakeResponse()

    monkeypatch.setattr("app.core.sms.httpx.post", fake_post)

    send_sms(settings, "9876543210", "hello")

    assert "Authorization" not in captured["headers"]
