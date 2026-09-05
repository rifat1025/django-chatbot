from django.core import signing
from django.conf import settings

SALT = "email-verification"


def generate_verification_token(user_id: int) -> str:
    return signing.dumps({"user_id": user_id}, salt=SALT)


def verify_token(token: str, max_age_seconds: int = 60 * 60 * 24):
    """Returns user_id if valid, raises signing.BadSignature/SignatureExpired otherwise."""
    data = signing.loads(token, salt=SALT, max_age=max_age_seconds)
    return data["user_id"]