from django.db import models
from django.conf import settings


class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255, db_index=True)
    sender_username = models.CharField(max_length=255)
    message = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

class Friendship(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                             on_delete=models.CASCADE, 
                             related_name='friendships')
    
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, 
                               on_delete=models.CASCADE, 
                               related_name='+')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user} → {self.friend}"


class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  related_name='sent_friend_requests')

    to_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='received_friend_requests')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.from_user} → {self.to_user}"