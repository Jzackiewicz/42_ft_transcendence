from django.contrib import admin

from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'difficulty', 'is_active', 'created_at']
    list_filter = ['difficulty', 'is_active']
    search_fields = ['text', 'canonical_answer']
    list_editable = ['is_active']
