from models import User
from users import authenticate, register_user


def test_user_registration_and_login() -> None:
    users: list[User] = []
    created = register_user(users, "Анна", "secret")
    assert created.id == 1
    assert authenticate(users, "анна", "secret") == created
    assert authenticate(users, "Анна", "wrong") is None
