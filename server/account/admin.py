from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SocialAccount

from .models import User, UserProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin for the custom User model, inheriting all default UserAdmin behaviour."""
    pass


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_online']
    list_filter = ['is_online']
    search_fields = ['user__username', 'user__email']


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "uid", "created_at")
    list_filter = ("provider",)
    search_fields = ("user__username", "user__email", "uid")
    readonly_fields = ("created_at",)
