from django.core.mail import send_mail
from django.conf import settings
from .utils import generate_verification_token


def send_verification_email(user, request=None):
    token = generate_verification_token(user.id)

    # Adjust FRONTEND_URL/domain to wherever your verify page actually lives
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    send_mail(
        subject="Verify your email",
        message=(
            f"Hi {user.username},\n\n"
            f"Please verify your email by visiting the link below:\n{verify_url}\n\n"
            f"This link expires in 24 hours."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )