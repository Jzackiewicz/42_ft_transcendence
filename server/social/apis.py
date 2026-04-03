from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .serializers import GetChatHistoryInputSerializer, GetChatHistoryOutputSerializer
from .selectors import get_chat_history_data
#from .services import 

"""
This module is for API endpoints, controllers, views.
In a Zero Trust architecture, this layer is responsible for handling incoming HTTP requests, validating them, and then delegating to the appropriate services or selectors.
It should not contain any business logic or direct database access; instead, it should focus on request/response handling and input validation.
"""

class ChatHistoryApi(APIView):
	
	@extend_schema(
		responses={200: GetChatHistoryOutputSerializer},
		description="GET endpoint to retrieve chatroom history."
	)
	def get(self, request):
		input_serializer = GetChatHistoryInputSerializer(data=request.query_params)
		input_serializer.is_valid(raise_exception=True)
		
		data = get_chat_history_data(**input_serializer.validated_data)
		
		output_serializer = GetChatHistoryOutputSerializer(data)
		return Response(output_serializer.data, status=status.HTTP_200_OK)