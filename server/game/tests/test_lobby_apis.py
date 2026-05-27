import uuid
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from game.models import GameSession, SessionPlayer

User = get_user_model()

class TestRoomCreateApi(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="testuser", email="test@test.com", password="password")

	def test_create_room_success(self):
		url = reverse('room-create')
		self.client.force_authenticate(user=self.user)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertIn('session_uuid', response.data)
		self.assertEqual(GameSession.objects.count(), 1)

	def test_create_room_unauthenticated(self):
		url = reverse('room-create')
		response = self.client.post(url)
		
		self.assertIn(
			response.status_code, 
			[status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
		)


class TestRoomJoinApi(APITestCase):
	def setUp(self):
		self.host = User.objects.create_user(username="host", email="host@test.com", password="password")
		self.player = User.objects.create_user(username="player", email="player@test.com", password="password")
		self.session = GameSession.objects.create(current_status=GameSession.Status.LOBBY)
		
		host_sp = SessionPlayer.objects.create(
			session=self.session,
			user=self.host,
			display_name="Host",
			seat_number=1
		)
		self.session.host_player = host_sp
		self.session.save()

	def test_join_room_success(self):
		url = reverse('room-join', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.player)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(self.session.session_players.count(), 2)

	def test_join_non_existent_room(self):
		fake_uuid = uuid.uuid4()
		url = reverse('room-join', kwargs={'session_uuid': fake_uuid})
		self.client.force_authenticate(user=self.player)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_join_started_room(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.save()

		url = reverse('room-join', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.player)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestRoomDestroyApi(APITestCase):
	def setUp(self):
		self.host = User.objects.create_user(username="host", email="host@test.com", password="password")
		self.player = User.objects.create_user(username="player", email="player@test.com", password="password")
		self.session = GameSession.objects.create(current_status=GameSession.Status.LOBBY)
		
		host_sp = SessionPlayer.objects.create(
			session=self.session,
			user=self.host,
			display_name="Host",
			seat_number=1
		)
		self.session.host_player = host_sp
		self.session.save()

	def test_destroy_room_success(self):
		url = reverse('room-destroy', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.host)
		response = self.client.delete(url)

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(GameSession.objects.count(), 0)

	def test_destroy_room_by_non_host(self):
		url = reverse('room-destroy', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.player)
		response = self.client.delete(url)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(GameSession.objects.count(), 1)