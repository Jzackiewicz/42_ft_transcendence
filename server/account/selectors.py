from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from .models import UserProfile

# ---------------------------------------------------------------------------
# User selectors
# ---------------------------------------------------------------------------

User = get_user_model()


def user_get_by_id(*, user_id: int) -> User:
    return get_object_or_404(User, id=user_id)


def user_get_by_username(*, username: str) -> User:
    return get_object_or_404(User, username=username)


def user_list() -> QuerySet:
    return User.objects.all()


# ---------------------------------------------------------------------------
# UserProfile selectors
# ---------------------------------------------------------------------------

def profile_get_by_id(*, profile_id: int) -> UserProfile:
    return get_object_or_404(UserProfile, id=profile_id)


def profile_get_by_user_id(*, user_id: int) -> UserProfile:
    return get_object_or_404(UserProfile, user_id=user_id)


def profile_get_by_username(*, username: str) -> UserProfile:
    return get_object_or_404(UserProfile, user__username=username)


def profile_list() -> QuerySet:
    return UserProfile.objects.all()


def profile_list_online() -> QuerySet:
    return UserProfile.objects.filter(is_online=True)

