from rest_framework import serializers


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
