class PresenceRegistry:
    _connections: dict[int, set[str]] = {}

    @classmethod
    def mark_online(cls, user_id: int, channel_name: str) -> bool:
        bucket = cls._connections.setdefault(user_id, set())
        was_empty = not bucket
        bucket.add(channel_name)
        return was_empty
    

    @classmethod
    def mark_offline(cls, user_id: int, channel_name: str) -> bool:
        bucket = cls._connections.get(user_id)
        if not bucket:
            return False
        bucket.discard(channel_name)
        if not bucket:
            del cls._connections[user_id]
            return True
        return False
    

    @classmethod
    def clear_user(cls, user_id: int):
        cls._connections.pop(user_id, None)

    
    @classmethod
    def is_online(cls, user_id: int) -> bool:
        return bool(cls._connections.get(user_id))
    

    @classmethod
    def online_user_ids(cls, user_ids: list[int]) -> set[int]:
        return { uid for uid in user_ids if cls._connections.get(uid) }
