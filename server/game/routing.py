from django.urls import path
from .consumers import GameConsumer


websocket_urlpatterns = [
    path('ws/game/<uuid:session_uuid>/', GameConsumer.as_asgi()),
]
