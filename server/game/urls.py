from django.urls import path
from game import apis

urlpatterns = [
	path('lobby/create/', apis.RoomCreateApi.as_view(), name='room-create'),
	path('lobby/join/<uuid:session_uuid>/', apis.RoomJoinApi.as_view(), name='room-join'),
	path('lobby/destroy/<uuid:session_uuid>/', apis.RoomDestroyApi.as_view(), name='room-destroy'),
	path('generate_extra_questions/', apis.GenerateExtraQuestionsApi.as_view(), name='generate-extra-questions'),
]