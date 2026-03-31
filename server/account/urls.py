"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from account import apis
from game import views
from .views import QuestionListView, UserListView, UserDetailsView

urlpatterns = [
    path('', apis.ExampleApi.as_view(), name='dbozic'),
    path('', views.dbozic, name='index'),
    path('appreciate/', views.async_appreciation, name='async_appreciation'),
    path('reason/', views.dbozic_charm, name='dbozic_charm'),
    path('questions/', QuestionListView.as_view(), name='question-list'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailsView.as_view(), name='user-detail'),
]
