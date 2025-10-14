from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Message, ChatRoom, UserPresence


@shared_task
def cleanup_expired_messages():
    """
    Clean up self-destructed messages that have expired
    """
    expired_messages = Message.objects.filter(
        self_destruct=True,
        destroy_after__lte=timezone.now(),
        is_deleted=False
    )
    
    count = expired_messages.count()
    
    # Soft delete expired messages
    for message in expired_messages:
        message.soft_delete()
    
    return f"Cleaned up {count} expired messages"


@shared_task
def send_message_notification(user_email, room_name, sender_username, message_preview):
    """
    Send email notification for new messages (when user is offline)
    """
    subject = f'New message in {room_name} - CipherTalk'
    message = f"""
    Hello,
    
    You have a new message from {sender_username} in the chat room '{room_name}':
    
    "{message_preview}"
    
    Login to CipherTalk to view and reply to the message.
    
    Best regards,
    The CipherTalk Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=True,
    )


@shared_task
def update_offline_users():
    """
    Update user presence - mark users as offline if they haven't been seen in a while
    """
    threshold = timezone.now() - timedelta(minutes=5)
    offline_users = UserPresence.objects.filter(
        online_status=True,
        last_seen__lte=threshold
    )
    
    count = offline_users.count()
    offline_users.update(online_status=False, typing_in=None)
    
    return f"Updated {count} users to offline status"


@shared_task
def send_daily_activity_summary():
    """
    Send daily activity summary to users (optional feature)
    """
    # This would be implemented based on user preferences
    # For now, it's a placeholder for future functionality
    pass


@shared_task
def backup_chat_data():
    """
    Backup chat data (placeholder for future implementation)
    """
    # This would export chat data to secure storage
    # Implementation depends on storage solution
    pass