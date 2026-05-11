from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserProfile

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
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class UserOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class UserUpdateInputSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)

    def validate_username(self, value):
        user = self.context.get("request").user
        if User.objects.filter(username=value).exclude(id=user.id).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def validate_email(self, value):
        user = self.context.get("request").user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


# ---------------------------------------------------------------------------
# UserProfile serializers
# ---------------------------------------------------------------------------


class UserProfileOutputSerializer(serializers.ModelSerializer):
    user = UserOutputSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "avatar", "is_online"]


class UserProfileAvatarInputSerializer(serializers.Serializer):
    avatar = serializers.ImageField()


class UserProfileFriendOutputSerializer(serializers.ModelSerializer):
    """Lightweight representation used when listing a profile's friends."""

    user = UserOutputSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "avatar", "is_online"]


# ---------------------------------------------------------------------------
# Login serializer
# ---------------------------------------------------------------------------


class UserLoginInputSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)  # never appear in output


class UserReauthSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
