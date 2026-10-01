from models import User
from users import authenticate, register_user
from utils import input_nonempty


def authenticate_user(users: list[User]) -> User | None:
    while True:
        action = input("\n1. Войти  2. Регистрация  0. Выход: ").strip()
        if action == "0":
            return None
        if action == "2":
            try:
                registered_user = register_user(
                    users, input_nonempty("Имя: "), input_nonempty("Пароль: "))
                print(f"Пользователь «{registered_user.name}» создан. Теперь войдите.")
            except ValueError as error:
                print(error)
        elif action == "1":
            authenticated_user = authenticate(
                users, input_nonempty("Имя: "), input_nonempty("Пароль: "))
            if authenticated_user is not None:
                return authenticated_user
            print("Неверное имя или пароль.")
        else:
            print("Неверный пункт меню.")
