from django.urls import path

from game import views

urlpatterns = [
    path('questions/', views.QuestionListApi.as_view(), name='question-list'),
    path('questions/<int:question_id>/', views.QuestionDetailApi.as_view(), name='question-detail'),
]
