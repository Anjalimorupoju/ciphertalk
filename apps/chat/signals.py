from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserPresence

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_presence(sender, instance, created, **kwargs):
    """
    Automatically create UserPresence when a new User is created
    """
    if created:
        UserPresence.objects.create(user=instance)