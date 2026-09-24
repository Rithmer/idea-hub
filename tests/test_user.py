from models import User
from users import authenticate, register_user


def test_user_registration_and_login() -> None:
    users: list[User] = []
    created = register_user(users, "Анна", "secret")
    assert created.id == 1
    assert authenticate(users, "анна", "secret") == created
    assert authenticate(users, "Анна", "wrong") is None


def test_legacy_unicode_password_and_invalid_hash() -> None:
    legacy = User(1, "Анна", "пароль")
    assert legacy.check_password("пароль")
    assert legacy.password.startswith("pbkdf2_sha256$")
    assert not legacy.check_password("неверный")
    malformed = User(2, "Борис", "pbkdf2_sha256$bad$salt$digest")
    assert not malformed.check_password("secret")
