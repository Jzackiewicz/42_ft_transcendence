from .models import ChatMessage


def get_chat_history_data(room_name: str, offset: int = 0) -> list[ChatMessage]:
    message_number_cap = 50
    messages = ChatMessage.objects.filter(room_name=room_name).order_by('-timestamp')[
        offset:offset + message_number_cap]
    return reversed(messages)
