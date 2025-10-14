from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from django.contrib import messages
import json
from .models import ChatRoom, Message, Contact, UserPresence
from apps.users.models import CustomUser, UserProfile


@login_required
def chat_dashboard(request):
    """Main chat dashboard with rooms and contacts"""
    # Get user's chat rooms
    chat_rooms = ChatRoom.objects.filter(
        participants=request.user,
        is_active=True
    ).annotate(
        message_count=Count('messages'),
        unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user))
    ).order_by('-messages__timestamp')
    
    # Get user's contacts
    contacts = Contact.objects.filter(user=request.user, is_blocked=False).select_related('contact_user')
    
    # Get online users
    online_users = UserPresence.objects.filter(online_status=True).exclude(user=request.user)
    
    context = {
        'chat_rooms': chat_rooms,
        'contacts': contacts,
        'online_users': online_users,
        'title': 'Chat Dashboard - CipherTalk'
    }
    return render(request, 'chat/dashboard.html', context)


@login_required
def chat_room(request, room_name):
    """Individual chat room view"""
    room = get_object_or_404(
        ChatRoom, 
        name=room_name, 
        participants=request.user,
        is_active=True
    )
    
    # Get messages for this room
    messages = Message.objects.filter(
        room=room,
        is_deleted=False
    ).select_related('sender', 'reply_to').order_by('timestamp')[:100]
    
    # Mark messages as read
    Message.objects.filter(
        room=room,
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)
    
    context = {
        'room': room,
        'messages': messages,
        'title': f'Chat - {room.name}'
    }
    return render(request, 'chat/chatroom.html', context)


@login_required
def create_room(request):
    """Create a new chat room"""
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        room_type = request.POST.get('room_type', 'private')
        participant_ids = request.POST.getlist('participants')
        
        if ChatRoom.objects.filter(name=room_name).exists():
            messages.error(request, 'A room with this name already exists.')
            return redirect('chat:dashboard')
        
        room = ChatRoom.objects.create(
            name=room_name,
            room_type=room_type,
            created_by=request.user
        )
        
        # Add participants
        room.participants.add(request.user)
        for user_id in participant_ids:
            try:
                user = CustomUser.objects.get(id=user_id)
                room.participants.add(user)
            except CustomUser.DoesNotExist:
                continue
        
        messages.success(request, f'Room "{room_name}" created successfully!')
        return redirect('chat:room', room_name=room.name)
    
    # GET request - show form
    users = CustomUser.objects.exclude(id=request.user.id)
    context = {
        'users': users,
        'title': 'Create Chat Room - CipherTalk'
    }
    return render(request, 'chat/create_room.html', context)


@login_required
def private_chat(request, username):
    """Create or access a private chat with another user"""
    other_user = get_object_or_404(CustomUser, username=username)
    
    if other_user == request.user:
        messages.error(request, "You cannot start a private chat with yourself.")
        return redirect('chat:dashboard')
    
    # Generate room name (sorted usernames to ensure uniqueness)
    usernames = sorted([request.user.username, other_user.username])
    room_name = f"private_{usernames[0]}_{usernames[1]}"
    
    # Get or create room
    room, created = ChatRoom.objects.get_or_create(
        name=room_name,
        defaults={
            'room_type': 'private',
            'created_by': request.user
        }
    )
    
    # Ensure both users are participants
    room.participants.add(request.user, other_user)
    
    if created:
        messages.success(request, f'Started private chat with {other_user.username}')
    
    return redirect('chat:room', room_name=room.name)


# API Views
@login_required
@require_http_methods(["GET"])
def room_list(request):
    """API: Get list of user's chat rooms"""
    rooms = ChatRoom.objects.filter(
        participants=request.user,
        is_active=True
    ).values('id', 'name', 'room_type', 'created_at')
    
    return JsonResponse({
        'rooms': list(rooms),
        'status': 'success'
    })


@login_required
@require_http_methods(["GET"])
def message_list(request, room_name):
    """API: Get messages for a room"""
    room = get_object_or_404(ChatRoom, name=room_name, participants=request.user)
    
    messages = Message.objects.filter(
        room=room,
        is_deleted=False
    ).select_related('sender', 'reply_to').order_by('timestamp')
    
    message_data = []
    for msg in messages:
        message_data.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'sender_id': msg.sender.id,
            'encrypted_content': msg.encrypted_content,
            'message_type': msg.message_type,
            'timestamp': msg.timestamp.isoformat(),
            'is_read': msg.is_read,
            'is_edited': msg.is_edited,
            'self_destruct': msg.self_destruct,
            'reply_to': msg.reply_to.id if msg.reply_to else None,
        })
    
    return JsonResponse({
        'messages': message_data,
        'room': room.name,
        'status': 'success'
    })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """API: Send a message"""
    try:
        data = json.loads(request.body)
        room_name = data.get('room_name')
        content = data.get('content')
        
        if not room_name or not content:
            return JsonResponse({'error': 'Room name and content are required'}, status=400)
        
        room = get_object_or_404(ChatRoom, name=room_name, participants=request.user)
        
        # Create message (encryption handled in model save)
        message = Message.objects.create(
            room=room,
            sender=request.user,
            encrypted_content=content,  # This should be encrypted on frontend
            iv=''  # IV from frontend encryption
        )
        
        return JsonResponse({
            'message_id': message.id,
            'status': 'success'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def contact_list(request):
    """API: Get user's contacts"""
    contacts = Contact.objects.filter(user=request.user, is_blocked=False).select_related('contact_user')
    
    contact_data = []
    for contact in contacts:
        contact_data.append({
            'id': contact.contact_user.id,
            'username': contact.contact_user.username,
            'email': contact.contact_user.email,
            'online': hasattr(contact.contact_user, 'presence') and contact.contact_user.presence.online_status,
            'nickname': contact.nickname,
        })
    
    return JsonResponse({
        'contacts': contact_data,
        'status': 'success'
    })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def add_contact(request):
    """API: Add a contact"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        
        if not username:
            return JsonResponse({'error': 'Username is required'}, status=400)
        
        contact_user = get_object_or_404(CustomUser, username=username)
        
        if contact_user == request.user:
            return JsonResponse({'error': 'Cannot add yourself as contact'}, status=400)
        
        # Check if contact already exists
        if Contact.objects.filter(user=request.user, contact_user=contact_user).exists():
            return JsonResponse({'error': 'Contact already exists'}, status=400)
        
        # Create contact
        contact = Contact.objects.create(
            user=request.user,
            contact_user=contact_user
        )
        
        return JsonResponse({
            'contact_id': contact.id,
            'username': contact_user.username,
            'status': 'success'
        })
        
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)