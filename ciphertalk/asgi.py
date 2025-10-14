import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciphertalk.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import apps.chat.routing

# DEBUG: This should print when runserver starts
print("🔄 ASGI APPLICATION LOADING...")
print("🔌 WebSocket patterns registered:")
for pattern in apps.chat.routing.websocket_urlpatterns:
    print(f"   {pattern.pattern}")
print("✅ ASGI ready for WebSocket connections")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.chat.routing.websocket_urlpatterns
        )
    ),
})