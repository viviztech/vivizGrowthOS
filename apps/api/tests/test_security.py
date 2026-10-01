from growthos.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_passwords_are_hashed_and_verified() -> None:
    hashed = hash_password("CorrectHorseBattery123!")
    assert "CorrectHorseBattery123!" not in hashed
    assert verify_password("CorrectHorseBattery123!", hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_carries_server_controlled_identity() -> None:
    token = create_access_token(user_id="user-1", tenant_id="tenant-1")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-1"
    assert payload["tenant_id"] == "tenant-1"
