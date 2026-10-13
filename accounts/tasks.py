from django.core.mail import send_mail
from celery import shared_task
from decouple import config

@shared_task
def send_otp_email(email, otp):
    subject="Your OTP Verification"
    message=(
        f"OTP is {otp}\n\n"
        "It is valid for 5 minutes"
    )
    from_email=config("EMAIL_HOST_USER")
    send_mail(
        subject,
        message,
        from_email,
        [email]
    )

@shared_task
def send_welcome_email(email,first_name):
    name=first_name or "there"
    subject="Welcome to Nixe"
    message = (
        f"Hi {name},\n\n"
        "Your account has been created successfully.\n\n"
        "🛍️ Happy shopping!\n\n"
        "Regards,\n"
        "The Nixe Team"
    )
    
    from_email=config("EMAIL_HOST_USER")
    send_mail(
        subject,
        message,
        from_email,
        [email]
    )

