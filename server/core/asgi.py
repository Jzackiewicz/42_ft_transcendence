"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

django_asgi_app = get_asgi_application()

# importing `routing` after calling `get_asgi_application` because it needs to load the settings first
import social.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# TODO: add authentication middleware for WebSocket (JWT token)
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        URLRouter(social.routing.websocket_urlpatterns)),
})
