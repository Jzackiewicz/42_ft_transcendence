from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import render


class DbozicView(APIView):
	"""
		View to show example how to create HTTP GET and POST endpoints. 
	"""
	def get(self, request, format=None):
		data = {"message": "I love Damian <3"}
		return Response(data, status=status.HTTP_200_OK)
	
	def post(self, request, format=None):
		incoming_data = request.data
		if incoming_data:
			data = {"message": "I got data.", "recieved": incoming_data}
			return Response(data, status=status.HTTP_201_CREATED)
		else:
			return Response({"message": "dupa"}, status=status.HTTP_400_BAD_REQUEST)
		

def async_appreciation(request):
	return (render(request, 'index.html'))