from .models import ChatMessage

def create_chat_message(room_name: str, sender_username: str, message: str) -> ChatMessage:
    chat_message = ChatMessage.objects.create(
        room_name=room_name,
        sender_username=sender_username,
        message=message
    )
    return chat_message