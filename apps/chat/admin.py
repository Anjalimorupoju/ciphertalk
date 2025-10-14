# apps/chat/admin.py
from django.contrib import admin
from .models import ChatRoom, Message, Contact, UserPresence

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'created_by', 'created_at', 'is_active')
    search_fields = ('name', 'created_by__username')
    list_filter = ('room_type', 'is_active')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'message_type', 'timestamp', 'is_read', 'is_deleted')
    search_fields = ('sender__username', 'room__name', 'encrypted_content')
    list_filter = ('is_read', 'is_deleted', 'message_type')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact_user', 'nickname', 'is_blocked')
    search_fields = ('user__username', 'contact_user__username', 'nickname')
    list_filter = ('is_blocked',)

@admin.register(UserPresence)
class UserPresenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'online_status', 'last_seen', 'typing_in')
    search_fields = ('user__username',)
    list_filter = ('online_status',)
