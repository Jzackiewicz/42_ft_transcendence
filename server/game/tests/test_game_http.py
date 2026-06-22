import uuid
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from game.models import GameSession, SessionPlayer, Question, SessionQuestion, AnswerAttempt

User = get_user_model()


@override_settings(QUESTIONS_PER_SESSION=10)
class TestRoomCreateApi(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="testuser", email="test@test.com", password="password")
		# Seed verified questions so that room creation succeeds
		for i in range(10):
			Question.objects.create(
				question_text=f"Question {i}?",
				correct_answer="Yes",
				category="general",
				is_verified=True
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
				category="general",
				is_verified=True
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


class TestUserGameStatsApis(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="testuser", email="test@test.com", password="password"
		)
		self.opponent = User.objects.create_user(
			username="opponent", email="opp@test.com", password="password"
		)
		self.no_game_user = User.objects.create_user(
			username="nogame", email="nogame@test.com", password="password"
		)

		# Create some questions
		self.q_history = Question.objects.create(
			question_text="Who was the first president of the US?",
			correct_answer="George Washington",
			category="History"
		)
		self.q_science = Question.objects.create(
			question_text="What is the chemical symbol for gold?",
			correct_answer="Au",
			category="Science"
		)
		self.q_geography = Question.objects.create(
			question_text="What is the capital of France?",
			correct_answer="Paris",
			category="Geography"
		)

	def test_get_stats_empty_user(self):
		self.client.force_authenticate(user=self.no_game_user)
		url = reverse('user-game-stats', kwargs={'user_id': self.no_game_user.id})
		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		data = response.data
		self.assertEqual(data['games_played'], 0)
		self.assertEqual(data['wins'], 0)
		self.assertEqual(data['win_rate'], 0.0)
		self.assertEqual(data['avg_score'], 0.0)
		self.assertEqual(data['total_points'], 0)
		self.assertEqual(data['highest_score'], 0)
		self.assertEqual(data['correct_rate'], 0.0)
		self.assertEqual(data['avg_answer_time_seconds'], 0.0)
		self.assertNotIn('timeouts_count', data)
		self.assertNotIn('games_hosted', data)
		self.assertNotIn('top_categories', data)

	def test_get_stats_with_games(self):
		# Game 1: Completed, user won, hosted by user
		session1 = GameSession.objects.create(
			current_status=GameSession.Status.GAME_OVER,
		)
		sp_user1 = SessionPlayer.objects.create(
			session=session1,
			user=self.user,
			display_name="User",
			seat_number=1,
			points=30,
			lives=3
		)
		sp_opp1 = SessionPlayer.objects.create(
			session=session1,
			user=self.opponent,
			display_name="Opponent",
			seat_number=2,
			points=10,
			lives=0
		)
		session1.host_player = sp_user1
		session1.winner = sp_user1
		session1.save()

		# Setup questions and attempts for Game 1
		sq1_1 = SessionQuestion.objects.create(session=session1, question=self.q_history, order_index=0)
		sq1_2 = SessionQuestion.objects.create(session=session1, question=self.q_science, order_index=1)

		# User attempts: 1 correct (History), 1 incorrect/timeout (Science)
		AnswerAttempt.objects.create(
			session=session1,
			player=sp_user1,
			session_question=sq1_1,
			answer_text="George Washington",
			is_correct=True,
			is_timeout=False,
			evaluation_status=AnswerAttempt.EvaluationStatus.EVALUATED,
			answer_time_ms=1500
		)
		AnswerAttempt.objects.create(
			session=session1,
			player=sp_user1,
			session_question=sq1_2,
			answer_text=None,
			is_correct=False,
			is_timeout=True,
			evaluation_status=AnswerAttempt.EvaluationStatus.EVALUATED,
			answer_time_ms=20000
		)

		# Game 2: Completed, opponent won, hosted by opponent
		session2 = GameSession.objects.create(
			current_status=GameSession.Status.GAME_OVER,
		)
		sp_user2 = SessionPlayer.objects.create(
			session=session2,
			user=self.user,
			display_name="User",
			seat_number=1,
			points=15,
			lives=0
		)
		sp_opp2 = SessionPlayer.objects.create(
			session=session2,
			user=self.opponent,
			display_name="Opponent",
			seat_number=2,
			points=40,
			lives=2
		)
		session2.host_player = sp_opp2
		session2.winner = sp_opp2
		session2.save()

		# Setup questions and attempts for Game 2
		sq2_1 = SessionQuestion.objects.create(session=session2, question=self.q_geography, order_index=0)
		sq2_2 = SessionQuestion.objects.create(session=session2, question=self.q_science, order_index=1)

		# User attempts: 2 correct (Geography, Science)
		AnswerAttempt.objects.create(
			session=session2,
			player=sp_user2,
			session_question=sq2_1,
			answer_text="Paris",
			is_correct=True,
			is_timeout=False,
			evaluation_status=AnswerAttempt.EvaluationStatus.EVALUATED,
			answer_time_ms=3000
		)
		AnswerAttempt.objects.create(
			session=session2,
			player=sp_user2,
			session_question=sq2_2,
			answer_text="Au",
			is_correct=True,
			is_timeout=False,
			evaluation_status=AnswerAttempt.EvaluationStatus.EVALUATED,
			answer_time_ms=2500
		)

		# Game 3: Active (Lobby) - should be excluded from stats!
		session3 = GameSession.objects.create(
			current_status=GameSession.Status.LOBBY,
		)
		SessionPlayer.objects.create(
			session=session3,
			user=self.user,
			display_name="User",
			seat_number=1,
			points=100,
			lives=3
		)

		# Query statistics
		self.client.force_authenticate(user=self.user)
		url = reverse('user-game-stats', kwargs={'user_id': self.user.id})
		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		data = response.data

		# Assertions
		self.assertEqual(data['games_played'], 2)  # Game 1 & Game 2 (excluding Game 3 because it is in Lobby)
		self.assertEqual(data['wins'], 1)  # Only Game 1
		self.assertEqual(data['win_rate'], 50.0)
		self.assertEqual(data['total_points'], 45)  # 30 + 15
		self.assertEqual(data['avg_score'], 22.5)  # (30 + 15) / 2
		self.assertEqual(data['highest_score'], 30)  # max(30, 15)
		
		# User has 4 attempts across Game 1 and Game 2:
		# Game 1: 1 correct (1500ms), 1 timeout (20000ms)
		# Game 2: 1 correct (3000ms), 1 correct (2500ms)
		# Total attempts: 4. Correct: 3.
		self.assertEqual(data['correct_rate'], 75.0)  # 3/4

		# Average answer time: non-timeout attempts are 1500ms, 3000ms, 2500ms.
		# Avg = (1500 + 3000 + 2500) / 3 = 7000 / 3 = 2333.33ms = 2.33 seconds
		self.assertEqual(data['avg_answer_time_seconds'], 2.33)
		
		# Unwanted statistics should not be present
		self.assertNotIn('timeouts_count', data)
		self.assertNotIn('games_hosted', data)
		self.assertNotIn('top_categories', data)

	def test_get_other_user_stats(self):
		self.client.force_authenticate(user=self.opponent)
		url = reverse('user-game-stats', kwargs={'user_id': self.user.id})
		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['games_played'], 0)  # No completed games for user setup

	def test_unauthenticated_request(self):
		url = reverse('user-game-stats', kwargs={'user_id': self.user.id})
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
