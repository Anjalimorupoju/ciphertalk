from rest_framework import serializers
from .models import ChatRoom, Message, Contact


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class ChatRoomSerializer(serializers.ModelSerializer):
    participants_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'room_type', 'created_by_username',
            'created_at', 'is_active', 'participants_count', 'last_message'
        ]

    def get_participants_count(self, obj):
        return obj.participants.count()

    def get_last_message(self, obj):
        last_msg = obj.messages.filter(is_deleted=False).last()
        if last_msg:
            return {
                'content': last_msg.encrypted_content,
                'sender': last_msg.sender.username,
                'timestamp': last_msg.timestamp
            }
        return None


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    reply_to_sender = serializers.CharField(source='reply_to.sender.username', read_only=True, allow_null=True)

    class Meta:
        model = Message
        fields = [
            'id', 'room', 'sender_username', 'encrypted_content', 'iv',
            'message_type', 'timestamp', 'is_read', 'is_edited',
            'self_destruct', 'destroy_after', 'reply_to', 'reply_to_sender'
        ]
        read_only_fields = ['timestamp', 'is_read']


class ContactSerializer(serializers.ModelSerializer):
    contact_username = serializers.CharField(source='contact_user.username', read_only=True)
    contact_email = serializers.CharField(source='contact_user.email', read_only=True)
    contact_online = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            'id', 'contact_username', 'contact_email', 'contact_online',
            'created_at', 'is_blocked', 'nickname'
        ]

    def get_contact_online(self, obj):
        return hasattr(obj.contact_user, 'presence') and obj.contact_user.presence.online_status