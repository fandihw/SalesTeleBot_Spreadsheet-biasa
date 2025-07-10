# services/__init__.py
from config import ALLOWED_USER_IDS

def is_user_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USER_IDS