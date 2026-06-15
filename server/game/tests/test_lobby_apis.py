import uuid
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from game.models import GameSession, SessionPlayer, Question

User = get_user_model()

class TestRoomCreateApi(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="testuser", email="test@test.com", password="password")
		# Seed questions so that room creation succeeds
		for i in range(10):
			Question.objects.create(
				question_text=f"Question {i}?",
				correct_answer="Yes",
				category="general"
			)

	def test_create_room_success(self):
		url = reverse('room-create')
		self.client.force_authenticate(user=self.user)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertIn('session_uuid', response.data)
		self.assertEqual(GameSession.objects.count(), 1)

	def test_create_room_fails_when_no_questions(self):
		Question.objects.all().delete()
		url = reverse('room-create')
		self.client.force_authenticate(user=self.user)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("error", response.data)
		self.assertEqual(GameSession.objects.count(), 0)

	def test_create_room_fails_when_not_enough_questions(self):
		Question.objects.all().delete()
		for i in range(4):
			Question.objects.create(
				question_text=f"Question {i}?",
				correct_answer="Yes",
				category="general"
			)
		url = reverse('room-create')
		self.client.force_authenticate(user=self.user)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("error", response.data)
		self.assertEqual(GameSession.objects.count(), 0)

	def test_create_room_unauthenticated(self):
		url = reverse('room-create')
		response = self.client.post(url)
		
		self.assertIn(
			response.status_code, 
			[status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
		)

	def test_create_room_succeeds_and_leaves_other_active_rooms(self):
		# Create an active room where the user is already playing
		other_session = GameSession.objects.create(current_status=GameSession.Status.ANSWERING)
		player = SessionPlayer.objects.create(
			session=other_session,
			user=self.user,
			display_name="testuser",
			seat_number=1,
			disconnected_at=None
		)

		url = reverse('room-create')
		self.client.force_authenticate(user=self.user)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		player.refresh_from_db()
		self.assertEqual(player.lives, 0)
		self.assertIsNotNone(player.disconnected_at)

	def test_create_room_succeeds_and_leaves_grace_period_room(self):
		# User is in active game and disconnected, but grace period hasn't expired yet
		from django.utils import timezone
		other_session = GameSession.objects.create(current_status=GameSession.Status.ANSWERING)
		player = SessionPlayer.objects.create(
			session=other_session,
			user=self.user,
			display_name="testuser",
			seat_number=1,
			lives=3,
			disconnected_at=timezone.now()
		)

		url = reverse('room-create')
		self.client.force_authenticate(user=self.user)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		player.refresh_from_db()
		self.assertEqual(player.lives, 0)

	def test_create_room_succeeds_if_grace_period_expired_in_another_room(self):
		# User is in active game and disconnected, and grace period has expired
		from django.utils import timezone
		from datetime import timedelta
		other_session = GameSession.objects.create(current_status=GameSession.Status.ANSWERING)
		SessionPlayer.objects.create(
			session=other_session,
			user=self.user,
			display_name="testuser",
			seat_number=1,
			lives=3,
			disconnected_at=timezone.now() - timedelta(seconds=35)
		)

		url = reverse('room-create')
		self.client.force_authenticate(user=self.user)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_create_room_succeeds_if_dead_in_another_room(self):
		# User is in active game and disconnected, but they have 0 lives (already eliminated)
		from django.utils import timezone
		other_session = GameSession.objects.create(current_status=GameSession.Status.ANSWERING)
		SessionPlayer.objects.create(
			session=other_session,
			user=self.user,
			display_name="testuser",
			seat_number=1,
			lives=0,
			disconnected_at=timezone.now()
		)

		url = reverse('room-create')
		self.client.force_authenticate(user=self.user)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_create_room_succeeds_and_cleans_up_stale_lobby_sessions(self):
		# User is host in a stale lobby session (status LOBBY)
		stale_session = GameSession.objects.create(current_status=GameSession.Status.LOBBY)
		stale_player = SessionPlayer.objects.create(
			session=stale_session,
			user=self.user,
			display_name="testuser",
			seat_number=1
		)
		stale_session.host_player = stale_player
		stale_session.save()

		# User is also a player in another stale lobby session (status LOBBY) where they are NOT the host
		other_host = User.objects.create_user(username="otherhost", email="other@test.com", password="password")
		stale_session2 = GameSession.objects.create(current_status=GameSession.Status.LOBBY)
		host_player = SessionPlayer.objects.create(
			session=stale_session2,
			user=other_host,
			display_name="otherhost",
			seat_number=1
		)
		stale_session2.host_player = host_player
		stale_session2.save()
		
		# Now add our user to stale_session2
		stale_player2 = SessionPlayer.objects.create(
			session=stale_session2,
			user=self.user,
			display_name="testuser",
			seat_number=2
		)

		# Make sure both stale lobby sessions exist before API call
		self.assertTrue(GameSession.objects.filter(id=stale_session.id).exists())
		self.assertTrue(GameSession.objects.filter(id=stale_session2.id).exists())
		self.assertEqual(stale_session2.session_players.count(), 2)

		# Request to create a new room
		url = reverse('room-create')
		self.client.force_authenticate(user=self.user)
		response = self.client.post(url)

		# The request should succeed
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		# The stale_session (where user was host and only player) should be deleted
		self.assertFalse(GameSession.objects.filter(id=stale_session.id).exists())

		# The stale_session2 (where user was a guest player) should NOT be deleted
		self.assertTrue(GameSession.objects.filter(id=stale_session2.id).exists())
		# But our user should be removed from stale_session2
		self.assertEqual(stale_session2.session_players.count(), 1)
		self.assertFalse(stale_session2.session_players.filter(user=self.user).exists())


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

	def test_join_started_room_succeeds_as_spectator(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.save()

		url = reverse('room-join', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.player)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIsNone(response.data['seat_number'])
		self.assertEqual(response.data['lives'], 0)

	def test_rejoin_active_room_success(self):
		SessionPlayer.objects.create(
			session=self.session,
			user=self.player,
			display_name="Player",
			seat_number=2
		)
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.save()

		url = reverse('room-join', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.player)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(self.session.session_players.count(), 2)

	def test_rejoin_completed_room_fails(self):
		SessionPlayer.objects.create(
			session=self.session,
			user=self.player,
			display_name="Player",
			seat_number=2
		)
		self.session.current_status = GameSession.Status.GAME_OVER
		self.session.save()

		url = reverse('room-join', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.player)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("Cannot join a game that has already ended.", response.data["error"])

	def test_join_room_succeeds_and_leaves_other_active_rooms(self):
		# User is active in another room (disconnected_at=None, current_status != GAME_OVER)
		other_session = GameSession.objects.create(current_status=GameSession.Status.ANSWERING)
		player = SessionPlayer.objects.create(
			session=other_session,
			user=self.player,
			display_name="Player",
			seat_number=1,
			disconnected_at=None
		)

		url = reverse('room-join', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.player)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		player.refresh_from_db()
		self.assertEqual(player.lives, 0)
		self.assertIsNotNone(player.disconnected_at)

	def test_join_room_succeeds_and_leaves_grace_period_room(self):
		# User is in active game and disconnected, but grace period hasn't expired yet
		from django.utils import timezone
		other_session = GameSession.objects.create(current_status=GameSession.Status.ANSWERING)
		player = SessionPlayer.objects.create(
			session=other_session,
			user=self.player,
			display_name="Player",
			seat_number=1,
			lives=3,
			disconnected_at=timezone.now()
		)

		url = reverse('room-join', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.player)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		player.refresh_from_db()
		self.assertEqual(player.lives, 0)

	def test_join_room_succeeds_if_grace_period_expired_in_another_room(self):
		# User is in active game and disconnected, and grace period has expired
		from django.utils import timezone
		from datetime import timedelta
		other_session = GameSession.objects.create(current_status=GameSession.Status.ANSWERING)
		SessionPlayer.objects.create(
			session=other_session,
			user=self.player,
			display_name="Player",
			seat_number=1,
			lives=3,
			disconnected_at=timezone.now() - timedelta(seconds=35)
		)

		url = reverse('room-join', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.player)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(self.session.session_players.count(), 2)

	def test_join_room_succeeds_if_dead_in_another_room(self):
		# User is in active game and disconnected, but they have 0 lives (already eliminated)
		from django.utils import timezone
		other_session = GameSession.objects.create(current_status=GameSession.Status.ANSWERING)
		SessionPlayer.objects.create(
			session=other_session,
			user=self.player,
			display_name="Player",
			seat_number=1,
			lives=0,
			disconnected_at=timezone.now()
		)

		url = reverse('room-join', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.player)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(self.session.session_players.count(), 2)




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

	def test_join_room_already_joined_returns_existing_player(self):
		SessionPlayer.objects.create(
			session=self.session,
			user=self.player,
			display_name="Player",
			seat_number=2
		)
		url = reverse('room-join', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.player)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(self.session.session_players.filter(user=self.player).count(), 1)

	def test_join_full_room_succeeds_as_spectator(self):
		self.session.max_players = 1
		self.session.save()

		url = reverse('room-join', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.player)
		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIsNone(response.data['seat_number'])
		self.assertEqual(response.data['lives'], 0)

	def test_join_room_unauthenticated(self):
		url = reverse('room-join', kwargs={'session_uuid': self.session.session_uuid})
		response = self.client.post(url)

		self.assertIn(
			response.status_code,
			[status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
		)

	def test_destroy_room_unauthenticated(self):
		url = reverse('room-destroy', kwargs={'session_uuid': self.session.session_uuid})
		response = self.client.delete(url)

		self.assertIn(
			response.status_code,
			[status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
		)
		self.assertEqual(GameSession.objects.count(), 1)

	def test_destroy_non_existent_room(self):
		fake_uuid = uuid.uuid4()
		url = reverse('room-destroy', kwargs={'session_uuid': fake_uuid})
		self.client.force_authenticate(user=self.host)
		response = self.client.delete(url)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_destroy_started_room(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.save()

		url = reverse('room-destroy', kwargs={'session_uuid': self.session.session_uuid})
		self.client.force_authenticate(user=self.host)
		response = self.client.delete(url)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(GameSession.objects.count(), 1)
