from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a new CustomUser is created
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Automatically save the UserProfile when the CustomUser is saved
    """
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # If profile doesn't exist, create it
        UserProfile.objects.create(user=instance)