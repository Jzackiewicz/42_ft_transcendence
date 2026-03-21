from django.shortcuts import render, HttpResponse

# Create your views here.
def dbozic(request):
    return (HttpResponse("I love Damian <3"))

def dbozic_charm(request):
    return (HttpResponse("He has a pretty smile <3"))