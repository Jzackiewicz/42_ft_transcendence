from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .serializers import GetExampleInputSerializer, GetExampleOutputSerializer, PostExampleInputSerializer, PostExampleOutputSerializer
from .selectors import get_example_data
from .services import create_example_record

"""
This module is for API endpoints, controllers, views.
In a Zero Trust architecture, this layer is responsible for handling incoming HTTP requests, validating them, and then delegating to the appropriate services or selectors.
It should not contain any business logic or direct database access; instead, it should focus on request/response handling and input validation.
"""

class ExampleApi(APIView):
	
	@extend_schema(
		parameters=[GetExampleInputSerializer],
		responses={200: GetExampleOutputSerializer},
		description="Example GET endpoint to retrieve data."
	)
	def get(self, request):
		input_serializer = GetExampleInputSerializer(data=request.query_params)
		input_serializer.is_valid(raise_exception=True)
		
		data = get_example_data(**input_serializer.validated_data)
		
		output_serializer = GetExampleOutputSerializer(data)
		return Response(output_serializer.data, status=status.HTTP_200_OK)
	
	@extend_schema(
		request=PostExampleInputSerializer,
		responses={201: PostExampleOutputSerializer},
		description="Example POST endpoint to create a new record."
	)
	def post(self, request):
		input_serializer = PostExampleInputSerializer(data=request.data)
		input_serializer.is_valid(raise_exception=True)
		
		result = create_example_record(**input_serializer.validated_data)
		
		output_serializer = PostExampleOutputSerializer(result)
		return Response(output_serializer.data, status=status.HTTP_201_CREATED)