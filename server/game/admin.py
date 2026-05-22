from django.contrib import admin
from .models import GameSession, SessionPlayer, Question, SessionQuestion, AnswerAttempt

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('session_uuid', 'current_status', 'host_player', 'created_at')
    list_filter = ('current_status',)
    search_fields = ('session_uuid',)
    readonly_fields = ('session_uuid',)

@admin.register(SessionPlayer)
class SessionPlayerAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'session', 'user', 'seat_number', 'lives', 'points')
    list_filter = ('lives', 'player_type')
    search_fields = ('display_name', 'user__username')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'category', 'correct_answer')
    list_filter = ('category',)
    search_fields = ('question_text',)

@admin.register(SessionQuestion)
class SessionQuestionAdmin(admin.ModelAdmin):
    list_display = ('session', 'question', 'order_index')

@admin.register(AnswerAttempt)
class AnswerAttemptAdmin(admin.ModelAdmin):
    list_display = ('session', 'player', 'evaluation_status', 'is_correct', 'is_timeout')
    list_filter = ('evaluation_status', 'is_correct', 'is_timeout')