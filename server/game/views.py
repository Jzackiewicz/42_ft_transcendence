from django.shortcuts import render, HttpResponse
from rest_framework import generics
from django.contrib.auth.models import User
from .models import Question
from .serializers import QuestionSerializer, UserSerializer

# Create your views here.
def dbozic(request):
    return (HttpResponse("I love Damian <3"))

def dbozic_charm(request):
    return (HttpResponse("He has a pretty smile <3"))

def async_appreciation(request):
    return (render(request, 'index.html'))

class QuestionListView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetailsView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer