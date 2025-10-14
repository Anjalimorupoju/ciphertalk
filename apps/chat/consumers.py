import json
import urllib.parse
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.utils import timezone
from .models import ChatRoom, Message, UserPresence
from .encryption import encryption_manager

print("🚨 CHAT CONSUMER MODULE LOADED - FILE IS EXECUTING!")

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        print("🚨 CHAT CONSUMER INSTANCE CREATED!")
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None
        self.user = None
        self.room = None

    async def connect(self):
        print("=" * 60)
        print("🚨 WEB SOCKET CONNECT METHOD CALLED!")
        print("=" * 60)
        
        try:
            # EMERGENCY DEBUGGING - Print everything in scope
            print(f"🚨 Scope keys: {list(self.scope.keys())}")
            print(f"🚨 Full path: {self.scope.get('path')}")
            print(f"🚨 Method: {self.scope.get('method')}")
            print(f"🚨 Headers: {self.scope.get('headers')}")
            
            # Get and URL-decode the room name
            encoded_room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_name = urllib.parse.unquote(encoded_room_name)
            self.room_group_name = f'chat_{self.room_name}'
            self.user = self.scope['user']

            print(f"🔗 WebSocket connecting to room: '{self.room_name}'")
            print(f"🔗 Decoded from: '{encoded_room_name}'")
            print(f"🔗 User: {self.user}")
            print(f"🔗 User authenticated: {self.user.is_authenticated}")
            print(f"🔗 User anonymous: {self.user.is_anonymous}")
            print(f"🔗 User username: {getattr(self.user, 'username', 'NO USERNAME')}")

            if self.user.is_anonymous:
                print("❌ REJECTED: User is anonymous")
                await self.close(code=4001)
                return

            # Get room from database
            print(f"🔍 Looking up room in database: '{self.room_name}'")
            self.room = await self.get_room(self.room_name)
            if not self.room:
                print(f"❌ REJECTED: Room not found: '{self.room_name}'")
                await self.close(code=4002)
                return
                
            print(f"✅ Room found: {self.room.name}")

            # Check if user is participant
            print(f"🔍 Checking if user is participant...")
            is_participant = await self.is_participant(self.room, self.user)
            print(f"🔍 Participant result: {is_participant}")
            
            if not is_participant:
                print(f"❌ REJECTED: User is not a participant")
                await self.close(code=4003)
                return

            # Join room group
            print(f"🔗 Joining room group: {self.room_group_name}")
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # Update user presence
            print("👤 Updating user presence...")
            await self.update_user_presence(True)

            print("✅ ACCEPTING WebSocket connection...")
            await self.accept()
            print("🎉 WEB SOCKET CONNECTION SUCCESSFUL!")
            print(f"✅ WebSocket connected to: {self.room_name}")

            # Send join notification
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'timestamp': timezone.now().isoformat(),
                }
            )
            print("📢 Join notification sent")

        except Exception as e:
            print(f"💥 CONNECTION ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            await self.close(code=4000)

    async def disconnect(self, close_code):
        print(f"🔌 WebSocket disconnected from: {self.room_name}, code: {close_code}")
        try:
            # Leave room group
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )

            # Update user presence
            if self.user and not self.user.is_anonymous:
                await self.update_user_presence(False)

                # Send leave notification
                if hasattr(self, 'room_group_name'):
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'user_left',
                            'user_id': self.user.id,
                            'username': self.user.username,
                            'timestamp': timezone.now().isoformat(),
                        }
                    )
                    
        except Exception as e:
            print(f"❌ WebSocket disconnect error: {e}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'chat_message')

            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'typing_start':
                await self.handle_typing_start()
            elif message_type == 'typing_stop':
                await self.handle_typing_stop()
            elif message_type == 'message_read':
                await self.handle_message_read(text_data_json)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'Invalid JSON'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': str(e)
            }))

    async def handle_chat_message(self, data):
        """Handle incoming chat messages"""
        message_content = data.get('message', '').strip()
        reply_to_id = data.get('reply_to')
        self_destruct = data.get('self_destruct', False)
        destroy_minutes = data.get('destroy_minutes', 0)

        if not message_content:
            return

        # Create message in database
        message = await self.create_message(
            message_content, 
            reply_to_id, 
            self_destruct, 
            destroy_minutes
        )

        # Broadcast message to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': message.id,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'encrypted_content': message.encrypted_content,
                'iv': message.iv,
                'message_type': message.message_type,
                'timestamp': message.timestamp.isoformat(),
                'reply_to': reply_to_id,
                'self_destruct': self_destruct,
            }
        )

    async def handle_typing_start(self):
        """Handle typing start event"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'username': self.user.username,
                'typing': True
            }
        )

    async def handle_typing_stop(self):
        """Handle typing stop event"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'username': self.user.username,
                'typing': False
            }
        )

    async def handle_message_read(self, data):
        """Handle message read receipts"""
        message_id = data.get('message_id')
        if message_id:
            await self.mark_message_as_read(message_id)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_read',
                    'message_id': message_id,
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
            )

    # Handler methods for different message types
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'encrypted_content': event['encrypted_content'],
            'iv': event['iv'],
            'message_type': event['message_type'],
            'timestamp': event['timestamp'],
            'reply_to': event.get('reply_to'),
            'self_destruct': event.get('self_destruct', False),
        }))

    async def user_joined(self, event):
        """Send user joined notification"""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))

    async def user_left(self, event):
        """Send user left notification"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))

    async def typing_indicator(self, event):
        """Send typing indicator"""
        await self.send(text_data=json.dumps({
            'type': 'typing_indicator',
            'user_id': event['user_id'],
            'username': event['username'],
            'typing': event['typing'],
        }))

    async def message_read(self, event):
        """Send message read receipt"""
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'username': event['username'],
        }))

    # Database operations - WITH DEBUGGING
    @database_sync_to_async
    def get_room(self, room_name):
        try:
            print(f"🔍 DATABASE: Looking for room '{room_name}'")
            room = ChatRoom.objects.get(name=room_name, is_active=True)
            print(f"✅ DATABASE: Room found - '{room.name}' (ID: {room.id})")
            
            # Debug participants
            participants = list(room.participants.all())
            print(f"👥 Room participants: {[p.username for p in participants]}")
            
            return room
        except ChatRoom.DoesNotExist:
            print(f"❌ DATABASE: Room '{room_name}' not found or not active")
            
            # List all available rooms for debugging
            all_rooms = ChatRoom.objects.filter(is_active=True)
            print(f"📋 Available active rooms: {[r.name for r in all_rooms]}")
            return None
        except Exception as e:
            print(f"💥 DATABASE ERROR: {e}")
            return None

    @database_sync_to_async
    def is_participant(self, room, user):
        result = room.participants.filter(id=user.id).exists()
        print(f"🔍 DATABASE: Participant check - User {user.username} in room {room.name}: {result}")
        return result

    @database_sync_to_async
    def create_message(self, content, reply_to_id, self_destruct, destroy_minutes):
        # Encrypt message
        encryption_result = encryption_manager.aes_cipher.encrypt(content)
        
        # Calculate destroy time if self-destruct is enabled
        destroy_after = None
        if self_destruct and destroy_minutes > 0:
            destroy_after = timezone.now() + timezone.timedelta(minutes=destroy_minutes)

        # Get reply message if provided
        reply_to = None
        if reply_to_id:
            try:
                reply_to = Message.objects.get(id=reply_to_id, room=self.room)
            except Message.DoesNotExist:
                pass

        message = Message.objects.create(
            room=self.room,
            sender=self.user,
            encrypted_content=encryption_result,
            iv='',  # IV is included in the encrypted_content
            reply_to=reply_to,
            self_destruct=self_destruct,
            destroy_after=destroy_after,
        )
        return message

    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id, room=self.room)
            message.mark_as_read()
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def update_user_presence(self, online):
        presence, created = UserPresence.objects.get_or_create(user=self.user)
        presence.online_status = online
        if not online:
            presence.typing_in = None
        presence.save()