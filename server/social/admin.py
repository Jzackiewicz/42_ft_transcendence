from django.contrib import admin
from .models import ChatMessage, Friendship, FriendRequest


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'sender_username', 'message', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('room_name', 'sender_username', 'message')
    readonly_fields = ('timestamp',)


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'created_at')
    search_fields = ('user__username', 'friend__username')
    readonly_fields = ('created_at',)


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')
    readonly_fields = ('created_at',)
