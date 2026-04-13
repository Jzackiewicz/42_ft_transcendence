from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from .models import Question

"""
Question read-only queries live here.
"""


def question_get_by_id(*, question_id: int) -> Question:
    return get_object_or_404(Question, id=question_id)


def question_list() -> QuerySet:
    """Return only active questions."""
    return Question.objects.filter(is_active=True)


def question_random() -> Question | None:
    """Return a single random active question, or None if none exist."""
    return Question.objects.filter(is_active=True).order_by('?').first()
