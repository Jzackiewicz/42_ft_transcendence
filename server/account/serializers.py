from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserProfile

class GetExampleInputSerializer(serializers.Serializer):
    param = serializers.CharField(max_length=200, required=False, default=None)


class PostExampleInputSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=200)
    mood_grade = serializers.IntegerField(min_value=1, max_value=10)


class GetExampleOutputSerializer(serializers.Serializer):
    message = serializers.CharField()
    datetime_called = serializers.DateTimeField()


class PostExampleOutputSerializer(serializers.Serializer):
    message = serializers.CharField()
    users_mood = serializers.CharField()
    datetime_called = serializers.DateTimeField()


# ---------------------------------------------------------------------------
# User serializers
# Serializers validate data only; all creation/mutation logic lives in
# services.py and is never embedded here.
# ---------------------------------------------------------------------------

User = get_user_model()


class UserRegisterInputSerializer(serializers.Serializer):
    """Input for user registration — validated data is passed to user_create()."""
    username = serializers.CharField(max_length=150, min_length=3)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class UserOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class UserUpdateInputSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)


# ---------------------------------------------------------------------------
# UserProfile serializers
# ---------------------------------------------------------------------------

class UserProfileOutputSerializer(serializers.ModelSerializer):
    user = UserOutputSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'avatar', 'is_online']


class UserProfileAvatarInputSerializer(serializers.Serializer):
    avatar = serializers.ImageField()


class UserProfileFriendOutputSerializer(serializers.ModelSerializer):
    """Lightweight representation used when listing a profile's friends."""
    user = UserOutputSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'avatar', 'is_online']
