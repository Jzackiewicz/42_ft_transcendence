from rest_framework import serializers

class DbozicSerializer(serializers.Serializer):
	message = serializers.CharField(max_length=200)
	recieved = serializers.DictField(child=serializers.CharField(), required=False)