from rest_framework import serializers

class ChatMessageSerializer(serializers.Serializer):
	message = serializers.CharField(max_length=500)

class GetChatHistoryInputSerializer(serializers.Serializer):
	offset = serializers.IntegerField(required=False, min_value=0, default=0)

class GetChatHistoryOutputSerializer(serializers.Serializer):
    message = serializers.CharField()
    sender_username = serializers.CharField()
    timestamp = serializers.DateTimeField()