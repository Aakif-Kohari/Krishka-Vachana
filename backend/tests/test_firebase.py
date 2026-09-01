from app.core.config import Settings


def test_emulator_hosts_fall_back_to_shared_convenience_setting():
    settings = Settings(firebase_emulator_host="localhost:9199")
    assert settings.firestore_emulator_host_effective == "localhost:9199"
    assert settings.firebase_auth_emulator_host_effective == "localhost:9199"


def test_emulator_hosts_can_be_overridden_independently():
    settings = Settings(
        firebase_emulator_host="localhost:9199",
        firestore_emulator_host="localhost:8080",
        firebase_auth_emulator_host="localhost:9099",
    )
    assert settings.firestore_emulator_host_effective == "localhost:8080"
    assert settings.firebase_auth_emulator_host_effective == "localhost:9099"


def test_emulator_hosts_default_to_empty():
    settings = Settings()
    assert settings.firestore_emulator_host_effective == ""
    assert settings.firebase_auth_emulator_host_effective == ""
