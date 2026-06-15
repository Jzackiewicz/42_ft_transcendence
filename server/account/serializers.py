from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserProfile
from .presence import PresenceRegistry

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
        user = self.context.get("user") or self.context.get("request").user
        if User.objects.filter(username=value).exclude(id=user.id).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def validate_email(self, value):
        user = self.context.get("user") or self.context.get("request").user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


# ---------------------------------------------------------------------------
# UserProfile serializers
# ---------------------------------------------------------------------------

# me
class UserProfileOutputSerializer(serializers.ModelSerializer):
    user = UserOutputSerializer(read_only=True)
    is_online = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["id", "user", "avatar", "is_online"]

    def get_is_online(self, profile):
        # Source of truth is the in-process registry — same as PublicUserSerializer.
        return PresenceRegistry.is_online(profile.user_id)


# expose to other users
class PublicUserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "avatar", "is_online"]

    def get_avatar(self, user):
        return user.profile.avatar_url(self.context.get("request"))
    
    def get_is_online(self, user):
        precomputed = self.context.get("online_user_ids")
        if precomputed is not None:
            return user.id in precomputed
        return PresenceRegistry.is_online(user.id)

class UserProfileAvatarInputSerializer(serializers.Serializer):
    avatar = serializers.ImageField()


# ---------------------------------------------------------------------------
# Login serializer
# ---------------------------------------------------------------------------


class UserLoginInputSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)  # never appear in output


class UserReauthSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
