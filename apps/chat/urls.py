from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Chat pages
    path('', views.chat_dashboard, name='dashboard'),
    path('room/<str:room_name>/', views.chat_room, name='room'),
    path('create-room/', views.create_room, name='create_room'),
    path('private-chat/<str:username>/', views.private_chat, name='private_chat'),
    
    # API endpoints
    path('api/rooms/', views.room_list, name='room_list'),
    path('api/messages/<str:room_name>/', views.message_list, name='message_list'),
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/contacts/', views.contact_list, name='contact_list'),
    path('api/add-contact/', views.add_contact, name='add_contact'),
]