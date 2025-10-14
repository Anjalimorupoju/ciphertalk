from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class ChatRoom(models.Model):
    ROOM_TYPE_CHOICES = [
        ('private', 'Private Chat'),
        ('group', 'Group Chat'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='private')
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # For group chats
    description = models.TextField(blank=True, null=True)
    max_participants = models.IntegerField(default=10)

    class Meta:
        db_table = 'chat_rooms'
        verbose_name = 'Chat Room'
        verbose_name_plural = 'Chat Rooms'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.room_type})"

    def get_participants_count(self):
        return self.participants.count()

    def get_last_message(self):
        return self.messages.filter(is_deleted=False).last()


class Message(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('file', 'File'),
        ('image', 'Image'),
        ('system', 'System Message'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Encrypted message content
    encrypted_content = models.TextField()
    iv = models.TextField()  # Initialization vector for AES encryption
    
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    # Message status
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    
    # Self-destruct feature
    self_destruct = models.BooleanField(default=False)
    destroy_after = models.DateTimeField(null=True, blank=True)
    
    # Reply functionality
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    
    # File attachments (if any)
    file_attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['room', 'timestamp']),
            models.Index(fields=['sender', 'timestamp']),
            models.Index(fields=['is_read', 'sender']),
        ]

    def __str__(self):
        return f"Message from {self.sender.username} in {self.room.name}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    def soft_delete(self):
        self.is_deleted = True
        self.encrypted_content = "[deleted]"
        self.iv = ""
        self.save()

    def is_expired(self):
        if self.self_destruct and self.destroy_after:
            return timezone.now() > self.destroy_after
        return False


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    contact_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_by')
    created_at = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table = 'user_contacts'
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        unique_together = ['user', 'contact_user']
        ordering = ['nickname', 'contact_user__username']

    def __str__(self):
        return f"{self.user.username} -> {self.contact_user.username}"


class UserPresence(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='presence')
    online_status = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    typing_in = models.ForeignKey(ChatRoom, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'user_presence'
        verbose_name = 'User Presence'
        verbose_name_plural = 'User Presence'

    def __str__(self):
        status = "Online" if self.online_status else "Offline"
        return f"{self.user.username} - {status}"