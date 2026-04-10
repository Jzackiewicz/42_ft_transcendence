from django.db import models
from statemachine.mixins import MachineMixin

class GameSession(MachineMixin, models.Model):
    current_state = models.CharField(max_length=50, default='lobby')

    players_count = models.IntegerField(default=0)
    target_player_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

class SessionPlayer(models.Model):
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='players')
    player_id = models.IntegerField()