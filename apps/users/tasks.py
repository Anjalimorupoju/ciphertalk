from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_welcome_email_task(user_email, username):
    """
    Send welcome email to new users
    """
    subject = 'Welcome to CipherTalk - Secure Chat Application'
    message = f"""
    Hello {username},
    
    Welcome to CipherTalk! We're excited to have you on board.
    
    With CipherTalk, you can:
    - Send encrypted messages to your contacts
    - Chat in real-time with friends
    - Enjoy complete privacy and security
    
    Get started by exploring your dashboard and adding contacts.
    
    If you have any questions, feel free to reach out to our support team.
    
    Best regards,
    The CipherTalk Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )


@shared_task
def send_otp_email_task(user_email, otp_code, otp_type):
    """
    Send OTP email for verification or 2FA
    """
    subject_map = {
        'email_verification': 'CipherTalk - Email Verification',
        'password_reset': 'CipherTalk - Password Reset',
        '2fa': 'CipherTalk - Two-Factor Authentication',
    }
    
    subject = subject_map.get(otp_type, 'CipherTalk - Security Code')
    
    message = f"""
    Your CipherTalk security code is: {otp_code}
    
    This code will expire in 10 minutes.
    
    If you didn't request this code, please ignore this email.
    
    Best regards,
    The CipherTalk Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )