import uuid
from django.db import models
from statemachine.mixins import MachineMixin
import game.fsm

class GameSession(MachineMixin, models.Model):
	session_uuid = models.UUIDField(default = uuid.uuid4, unique=True)
	
	current_status = models.CharField(max_length=50, default='Lobby')
	session_questions_ids = models.JSONField(default=list)
	current_player_id = models.IntegerField(null=True, blank=True)
	nominator_id = models.IntegerField(null=True, blank=True)
	current_question_id = models.IntegerField(null=True, blank=True)
	question_asked_count = models.IntegerField(default=0)
	
	player_answer = models.CharField(max_length=255, null=True, blank=True)
	player_answer_correct = models.BooleanField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	state_machine_name = 'game.fsm.GameStateMachine'
	state_machine_attr = 'fsm'
	state_field_name = 'current_status'

	class Meta:
		ordering = ['-created_at']

class SessionPlayer(models.Model):
	session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='session_players')
	
	player_id = models.IntegerField()
	name = models.CharField(max_length=100)
	lives = models.IntegerField(default=3)
	points = models.IntegerField(default=0)