from app.core.config import Settings


def test_emulator_hosts_fall_back_to_shared_convenience_setting():
    """Verify that emulator hosts fall back to the shared convenience setting."""
    settings = Settings(firebase_emulator_host="localhost:9199")
    assert settings.firestore_emulator_host_effective == "localhost:9199"
    assert settings.firebase_auth_emulator_host_effective == "localhost:9199"


def test_emulator_hosts_can_be_overridden_independently():
    """Verify that Firestore and Auth emulator hosts can be configured independently."""
    settings = Settings(
        firebase_emulator_host="localhost:9199",
        firestore_emulator_host="localhost:8080",
        firebase_auth_emulator_host="localhost:9099",
    )
    assert settings.firestore_emulator_host_effective == "localhost:8080"
    assert settings.firebase_auth_emulator_host_effective == "localhost:9099"


def test_emulator_hosts_default_to_empty():
    """Verify that emulator hosts default to empty when not configured."""
    settings = Settings()
    assert settings.firestore_emulator_host_effective == ""
    assert settings.firebase_auth_emulator_host_effective == ""
