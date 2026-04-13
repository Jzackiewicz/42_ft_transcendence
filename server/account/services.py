from datetime import datetime
from django.contrib.auth import get_user_model
from .models import UserProfile

# For POST, CREATE, UPDATE REQUESTS

def create_example_record(*, message: str, mood_grade: int) -> dict:
    if mood_grade < 4:
        users_mood = "Bad"
    elif mood_grade < 7:
        users_mood = "Neutral"
    else:
        users_mood = "Good"
    return {
        "message": f"POST ECHO: {message}",
        "users_mood": users_mood,
        "datetime_called": datetime.now().isoformat(),
    }


# ---------------------------------------------------------------------------
# User services
# CRUD
# ---------------------------------------------------------------------------

User = get_user_model()

def user_create(*, username: str, email: str, password: str) -> User:
    """Create and return a new user. Hashing password. UserProfile is created via signal."""
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )


def user_update_password(*, user: User, new_password: str) -> User:
    user.set_password(new_password)
    user.save(update_fields=['password'])
    return user


def user_update_basic_info(
    *,
    user: User,
    username: str | None = None,
    email: str | None = None,
) -> User:
    update_fields: list[str] = []
    if username is not None:
        user.username = username
        update_fields.append('username')
    if email is not None:
        user.email = email
        update_fields.append('email')
    if update_fields:
        user.save(update_fields=update_fields)
    return user


# ---------------------------------------------------------------------------
# UserProfile services
# ---------------------------------------------------------------------------

def profile_update_avatar(*, profile: UserProfile, avatar) -> UserProfile:
    profile.avatar = avatar
    profile.save(update_fields=['avatar'])
    return profile


def profile_clear_avatar(*, profile: UserProfile) -> UserProfile:
    profile.avatar = None
    profile.save(update_fields=['avatar'])
    return profile


def profile_set_online_status(*, profile: UserProfile, is_online: bool) -> UserProfile:
    profile.is_online = is_online
    profile.save(update_fields=['is_online'])
    return profile


def profile_add_friend(*, profile: UserProfile, friend_profile: UserProfile) -> None:
    if profile == friend_profile:
        raise ValueError("A user cannot add themselves as a friend.")
    profile.friends.add(friend_profile)


def profile_remove_friend(*, profile: UserProfile, friend_profile: UserProfile) -> None:
    profile.friends.remove(friend_profile)
