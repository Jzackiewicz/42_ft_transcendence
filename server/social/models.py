from django.db import models


class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255, db_index=True)
    sender_username = models.CharField(max_length=255)
    message = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
