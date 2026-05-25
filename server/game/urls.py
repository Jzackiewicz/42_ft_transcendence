from django.urls import path
from game import apis

urlpatterns = [
	path("questions/", apis.QuestionListApi.as_view(), name="question-list"),
	path("questions/<int:question_id>/", apis.QuestionDetailApi.as_view(), name="question-detail"),
	path("questions/generate/", apis.QuestionGenerateApi.as_view(), name="question-generate"),
]