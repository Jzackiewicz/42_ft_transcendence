import datetime
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .serializers import ChatMessageSerializer
from .services import create_chat_message
from .selectors import are_friends, other_user_in_dm, PRESENCE_ROOM
from account.presence import PresenceRegistry


PRESENCE_GROUP = "presence"


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.accept()
            await self.close(code=4001)
            return
        
        room_name = self.scope["url_route"]["kwargs"]["room_name"]
        if room_name != PRESENCE_ROOM:
            if not await self._can_access_dm(user.id, room_name):
                await self.accept()
                await self.close(code=4003)
                return

        self.room_name = room_name
        self.room_group_name = f"chat_{self.room_name}"

        await self.accept()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(PRESENCE_GROUP, self.channel_name)
        
        became_online = PresenceRegistry.mark_online(user.id, self.channel_name)
        if became_online:
            await self.channel_layer.group_send(
                PRESENCE_GROUP,
                {"type": "presence.update", "user_id": user.id, "is_online": True},
            )

    
    @database_sync_to_async
    def _can_access_dm(self, user_id: int, room_name: str) -> bool:
        other_id = other_user_in_dm(room_name=room_name, requester_id=user_id)
        if other_id is None:
            return False
        return are_friends(user_a_id=user_id, user_b_id=other_id)


    async def disconnect(self, close_code):
        # room_group_name is only set when an authenticated connection succeeded.
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        user = self.scope["user"]
        if user.is_authenticated:
            await self.channel_layer.group_discard(PRESENCE_GROUP, self.channel_name)
            became_offline = PresenceRegistry.mark_offline(user.id, self.channel_name)
            if became_offline:
                await self.channel_layer.group_send(
                    PRESENCE_GROUP,
                    {"type": "presence.update", "user_id": user.id, "is_online": False},
                )


    async def receive_json(self, content, **kwargs):
        input_serializer = ChatMessageSerializer(data=content)
        if not input_serializer.is_valid():
            await self.send_json({
                "error": "Invalid message format.",
                "details": input_serializer.errors
            })
            return

        user = self.scope["user"]
        if self.room_name != PRESENCE_ROOM:
            if not await self._can_access_dm(user.id, self.room_name):
                await self.send_json({"error": "You are no longer allowed in this room."})
                await self.close(code=4003)
                return
            
        message = input_serializer.validated_data["message"]
        sender = self.scope["user"].username

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender_username": sender,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            },
        )

        await database_sync_to_async(create_chat_message)(
            room_name=self.room_name, sender_username=sender, message=message)

    async def chat_message(self, event):
        message = event["message"]
        sender_username = event["sender_username"]
        timestamp = event["timestamp"]
        await self.send_json({
            "message": message,
            "sender_username": sender_username,
            "timestamp": timestamp,
        })


    async def presence_update(self, event):
        await self.send_json({
            "type": "presence.update",
            "user_id": event["user_id"],
            "is_online": event["is_online"],
        })
