from models import User


def get_user_by_id(users: list[User], user_id: int) -> User | None:

    return next((user for user in users if user.id == user_id), None)


def register_user(users: list[User], name: str, password: str) -> User:

    clean_name, clean_password = name.strip(), password.strip()
    if not clean_name or not clean_password:
        raise ValueError("имя и пароль не могут быть пустыми")
    if any(user.name.casefold() == clean_name.casefold() for user in users):
        raise ValueError("пользователь с таким именем уже существует")
    user = User(max((item.id for item in users), default=0) + 1,
                clean_name, clean_password)
    users.append(user)
    return user


def authenticate(users: list[User], name: str, password: str) -> User | None:

    return next(
        (user for user in users if user.name.casefold() == name.strip().casefold()
         and user.password == password.strip()),
        None,
    )
