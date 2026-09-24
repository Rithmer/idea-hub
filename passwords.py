from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_hex

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 200_000


def hash_password(password: str) -> str:
    salt = token_hex(16)
    digest = pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), ITERATIONS)
    return f"{ALGORITHM}${ITERATIONS}${salt}${digest.hex()}"


def verify_password(stored: str, password: str) -> bool:
    if not stored.startswith(f"{ALGORITHM}$"):
        return compare_digest(stored.encode(), password.encode())
    try:
        algorithm, rounds, salt, expected = stored.split("$")
        if algorithm != ALGORITHM or int(rounds) != ITERATIONS:
            return False
        digest = pbkdf2_hmac("sha256", password.encode(),
                             bytes.fromhex(salt), ITERATIONS)
        return compare_digest(digest, bytes.fromhex(expected))
    except ValueError:
        return False
