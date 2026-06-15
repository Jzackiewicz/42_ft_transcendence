from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack

from game.routing import websocket_urlpatterns
from game.models import GameSession, SessionPlayer, Question, SessionQuestion
from game.services.game_flow.game_action_handler import GameAction
from channels.db import database_sync_to_async

User = get_user_model()

class GameConsumerTests(TransactionTestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='testuser', 
			password='password',
			email='testuser@test.com'
		)
		self.unjoined_user = User.objects.create_user(
			username="unjoined",
			password="password",
			email="unjoined@test.com"
		)
		self.user2 = User.objects.create_user(
			username="testuser2",
			password="password",
			email="testuser2@test.com"
		)
		
		self.session = GameSession.objects.create(current_status=GameSession.Status.LOBBY, evaluation_time_limit_ms=0)
		self.player = SessionPlayer.objects.create(
			session=self.session,
			user=self.user,
			display_name="Test User",
			seat_number=1
		)
		self.player2 = SessionPlayer.objects.create(
			session=self.session,
			user=self.user2,
			display_name="Player 2",
			seat_number=2
		)
		
		self.session.host_player = self.player
		self.session.save()
		
		self.q1 = Question.objects.create(question_text="Test?", correct_answer="yes")
		SessionQuestion.objects.create(session=self.session, question=self.q1, order_index=0)
		
		self.client = Client()
		self.client.force_login(self.user)
		self.cookie = self.client.cookies.get('sessionid').value
		
		self.client2 = Client()
		self.client2.force_login(self.user2)
		self.cookie2 = self.client2.cookies.get('sessionid').value
		
		self.unjoined_client = Client()
		self.unjoined_client.force_login(self.unjoined_user)
		self.unjoined_cookie = self.unjoined_client.cookies.get('sessionid').value

		self.application = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))

	def tearDown(self):
		from channels.layers import get_channel_layer
		channel_layer = get_channel_layer()
		if hasattr(channel_layer, 'receive_clean_locks'):
			channel_layer.receive_clean_locks.locks.clear()
		super().tearDown()

	async def test_connect_success(self):
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		
		response = await communicator.receive_json_from()
		self.assertEqual(response["type"], "game_state_update")
		self.assertEqual(response["action"], "player_connected")
		self.assertIn("snapshot", response)
		await communicator.disconnect()

	async def test_connect_unauthenticated(self):
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/"
		)
		connected, _ = await communicator.connect()
		self.assertFalse(connected)

	async def test_connect_unjoined_user(self):
		headers = [(b'cookie', f'sessionid={self.unjoined_cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertFalse(connected)

	async def test_receive_missing_action(self):
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		await communicator.receive_json_from()
		await communicator.send_json_to({"payload": {}})
		response = await communicator.receive_json_from()
		self.assertIn("error", response)
		self.assertEqual(response["error"], "Action is required")
		await communicator.disconnect()

	async def test_receive_invalid_payload_format_returns_error(self):
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		await communicator.receive_json_from()
		
		await communicator.send_json_to({
			"action": GameAction.NOMINATE_PLAYER, 
			"payload": {}
		})
		response = await communicator.receive_json_from()
		
		self.assertIn("error", response)
		self.assertIn("target_player_id", response["error"])
		await communicator.disconnect()

	async def test_submit_answer_rejects_answer_text_payload_field(self):
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application,
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		await communicator.receive_json_from()

		await communicator.send_json_to({
			"action": GameAction.SUBMIT_ANSWER,
			"payload": {"answer_text": "wrong"}
		})
		response = await communicator.receive_json_from()

		self.assertIn("error", response)
		self.assertIn("answer_text", response["error"])
		await communicator.disconnect()

	async def test_action_domain_validation_error_returns_error_message(self):
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		await communicator.connect()
		await communicator.receive_json_from()
		
		await communicator.send_json_to({
			"action": GameAction.SUBMIT_ANSWER, 
			"payload": {"answer": "yes"}
		})
		response = await communicator.receive_json_from()
		
		self.assertEqual(response["type"], "error")
		self.assertIn("Game session is not in answering state", response["message"])
		await communicator.disconnect()

	async def test_successful_action_broadcasts_state_update(self):
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		await communicator.connect()
		await communicator.receive_json_from()
		
		await communicator.send_json_to({
			"action": GameAction.START_GAME, 
			"payload": {}
		})
		
		response = await communicator.receive_json_from()
		
		self.assertEqual(response["type"], "game_state_update")
		self.assertEqual(response["action"], GameAction.START_GAME)
		self.assertIn("snapshot", response)
		self.assertEqual(response["snapshot"]["current_status"], GameSession.Status.ANSWERING)
		self.assertIsNotNone(response["snapshot"]["current_attempt"])
		self.assertIsNotNone(response["snapshot"]["current_attempt_started_at"])
		self.assertIsNotNone(response["snapshot"]["turn_deadline_at"])
		await communicator.disconnect()

	async def test_answering_state_triggers_automatic_timeout_broadcast(self):
		q2 = await database_sync_to_async(Question.objects.create)(
			question_text="Test2?", correct_answer="no"
		)
		await database_sync_to_async(SessionQuestion.objects.create)(
			session=self.session, question=q2, order_index=1
		)

		self.session.answer_time_limit_ms = 100
		await database_sync_to_async(self.session.save)()
		
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		await communicator.connect()
		await communicator.receive_json_from()
		
		await communicator.send_json_to({
			"action": GameAction.START_GAME, 
			"payload": {}
		})
		
		start_response = await communicator.receive_json_from()
		self.assertEqual(start_response["action"], GameAction.START_GAME)
		
		timeout_response = await communicator.receive_json_from(timeout=2.0)
		self.assertEqual(timeout_response["type"], "game_state_update")
		self.assertEqual(timeout_response["action"], "evaluate_timeout")
		self.assertEqual(timeout_response["snapshot"]["current_status"], GameSession.Status.EVALUATION)

		# Wait for auto-resolution to transition to the next turn (answering)
		next_response = await communicator.receive_json_from(timeout=2.0)
		self.assertEqual(next_response["type"], "game_state_update")
		self.assertEqual(next_response["snapshot"]["current_status"], GameSession.Status.ANSWERING)
		
		await communicator.disconnect()

	async def test_evaluation_phase_duration_holds_state_and_transitions(self):
		q2 = await database_sync_to_async(Question.objects.create)(
			question_text="Test2?", correct_answer="no"
		)
		await database_sync_to_async(SessionQuestion.objects.create)(
			session=self.session, question=q2, order_index=1
		)

		self.session.evaluation_time_limit_ms = 400
		self.session.answer_time_limit_ms = 10000
		await database_sync_to_async(self.session.save)()

		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1
		)
		await comm1.connect()
		await comm1.receive_json_from()
		
		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers2
		)
		await comm2.connect()
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		await comm1.send_json_to({"action": GameAction.START_GAME})
		res_start = await comm1.receive_json_from()
		await comm2.receive_json_from()

		current_player_id = res_start["snapshot"]["current_player"]
		current_comm = comm1 if current_player_id == self.player.id else comm2
		other_comm = comm2 if current_player_id == self.player.id else comm1

		# Submit answer from the correct active player to trigger evaluation state
		await current_comm.send_json_to({
			"action": GameAction.SUBMIT_ANSWER,
			"payload": {"answer": "yes"}
		})

		# Immediately receive response - we should be in EVALUATION status
		eval_response = await current_comm.receive_json_from()
		await other_comm.receive_json_from()
		self.assertEqual(eval_response["type"], "game_state_update")
		self.assertEqual(eval_response["snapshot"]["current_status"], GameSession.Status.EVALUATION)

		# Verify that we do not transition immediately (wait 100ms and expect no message)
		# We use receive_nothing here because a timeout on receive_json_from would cancel/terminate the communicator.
		is_empty = await current_comm.receive_nothing(timeout=0.1)
		self.assertTrue(is_empty)

		# Wait for the transition to finish after evaluation timeout (400ms total, so wait up to 2.0s)
		finish_response = await current_comm.receive_json_from(timeout=2.0)
		await other_comm.receive_json_from()
		self.assertEqual(finish_response["type"], "game_state_update")
		self.assertEqual(finish_response["action"], "handle_evaluation_finish")
		self.assertEqual(finish_response["snapshot"]["current_status"], GameSession.Status.NOMINATION)

		await comm1.disconnect()
		await comm2.disconnect()

	async def test_websocket_disconnect_triggers_disconnect_broadcast_to_others(self):
		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1
		)
		await comm1.connect()
		await comm1.receive_json_from()
		
		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers2
		)
		await comm2.connect()
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		await comm1.send_json_to({"action": GameAction.START_GAME, "payload": {}})
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		await comm1.disconnect()

		disconnect_response = await comm2.receive_json_from(timeout=2.0)
		self.assertEqual(disconnect_response["type"], "game_state_update")
		self.assertEqual(disconnect_response["action"], GameAction.DISCONNECT)
		
		await comm2.disconnect()

	async def test_fast_answer_cancels_timeout_task(self):
		self.session.answer_time_limit_ms = 200
		await database_sync_to_async(self.session.save)()

		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers1
		)
		connected, _ = await comm1.connect()
		self.assertTrue(connected)
		await comm1.receive_json_from()

		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(
			self.application,
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers2
		)
		connected, _ = await comm2.connect()
		self.assertTrue(connected)
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		await comm1.send_json_to({"action": GameAction.START_GAME})
		start_response = await comm1.receive_json_from()
		await comm2.receive_json_from()
		current_player_id = start_response["snapshot"]["current_player"]
		current_communicator = comm1 if current_player_id == self.player.id else comm2
		
		await current_communicator.send_json_to({
			"action": GameAction.SUBMIT_ANSWER,
			"payload": {"answer": "yes"}
		})

		import asyncio
		await asyncio.sleep(0.6)

		evaluate_timeout_seen = False
		for communicator in (comm1, comm2):
			while not communicator.output_queue.empty():
				msg = await communicator.receive_json_from()
				if msg.get('action') == 'evaluate_timeout':
					evaluate_timeout_seen = True
					break

		self.assertFalse(evaluate_timeout_seen, 'Received stale evaluate_timeout event.')
		await comm1.disconnect()
		await comm2.disconnect()

	async def test_last_player_disconnect_deletes_session_gracefully(self):
		await database_sync_to_async(self.player2.delete)()
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		await communicator.receive_json_from()

		await communicator.disconnect()

		# Session should still exist because they disconnected gracefully
		session_exists = await database_sync_to_async(
			GameSession.objects.filter(id=self.session.id).exists
		)()
		self.assertTrue(session_exists)

		# Fast forward disconnected_at past the grace period
		from django.utils import timezone
		from datetime import timedelta
		from django.conf import settings
		grace_limit = timezone.now() - timedelta(seconds=settings.DISCONNECT_GRACE_PERIOD_S + 1)
		await database_sync_to_async(
			lambda: SessionPlayer.objects.filter(id=self.player.id).update(disconnected_at=grace_limit)
		)()

		# Expire players
		from game.services.game_flow.game_action_handler import GameActionHandler
		handler = GameActionHandler()
		await database_sync_to_async(handler.sync_game_disconnections)(self.session.id)

		# Session should now be deleted
		session_exists = await database_sync_to_async(
			GameSession.objects.filter(id=self.session.id).exists
		)()
		self.assertFalse(session_exists)

	async def test_websocket_nomination_flow(self):
		q2 = await database_sync_to_async(Question.objects.create)(
			question_text="Test2?", correct_answer="no"
		)
		await database_sync_to_async(SessionQuestion.objects.create)(
			session=self.session, question=q2, order_index=1
		)

		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1
		)
		await comm1.connect()
		await comm1.receive_json_from()
		
		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers2
		)
		await comm2.connect()
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		await comm1.send_json_to({"action": GameAction.START_GAME})
		res_start = await comm1.receive_json_from()
		await comm2.receive_json_from()
		
		current_player_id = res_start["snapshot"]["current_player"]
		current_comm = comm1 if current_player_id == self.player.id else comm2
		other_comm = comm2 if current_player_id == self.player.id else comm1
		other_player_id = self.player2.id if current_player_id == self.player.id else self.player.id
		
		# Submit correct answer to force a nomination turn
		await current_comm.send_json_to({
			"action": GameAction.SUBMIT_ANSWER,
			"payload": {"answer": "yes"}
		})
		res_eval = await current_comm.receive_json_from()
		await other_comm.receive_json_from()
		
		self.assertEqual(res_eval["snapshot"]["current_status"], GameSession.Status.EVALUATION)

		# Wait for auto-resolution to transition to nomination
		res_nom_phase = await current_comm.receive_json_from()
		await other_comm.receive_json_from()
		self.assertEqual(res_nom_phase["snapshot"]["current_status"], GameSession.Status.NOMINATION)
		
		# Nominate player
		await current_comm.send_json_to({
			"action": GameAction.NOMINATE_PLAYER,
			"payload": {"target_player_id": other_player_id}
		})
		
		res_nom = await current_comm.receive_json_from()
		await other_comm.receive_json_from()
		
		self.assertEqual(res_nom["type"], "game_state_update")
		self.assertEqual(res_nom["action"], GameAction.NOMINATE_PLAYER)
		self.assertEqual(res_nom["snapshot"]["current_status"], GameSession.Status.ANSWERING)
		self.assertEqual(res_nom["snapshot"]["current_player"], other_player_id)
		
		await comm1.disconnect()
		await comm2.disconnect()

	async def test_websocket_nomination_timeout(self):
		q2 = await database_sync_to_async(Question.objects.create)(
			question_text="Test2?", correct_answer="no"
		)
		await database_sync_to_async(SessionQuestion.objects.create)(
			session=self.session, question=q2, order_index=1
		)

		# Set a short nomination time limit to speed up test execution
		await database_sync_to_async(
			lambda: GameSession.objects.filter(id=self.session.id).update(
				nomination_time_limit_ms=100
			)
		)()

		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1
		)
		await comm1.connect()
		await comm1.receive_json_from()
		
		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers2
		)
		await comm2.connect()
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		await comm1.send_json_to({"action": GameAction.START_GAME})
		res_start = await comm1.receive_json_from()
		await comm2.receive_json_from()
		
		current_player_id = res_start["snapshot"]["current_player"]
		current_comm = comm1 if current_player_id == self.player.id else comm2
		other_comm = comm2 if current_player_id == self.player.id else comm1
		
		# Submit correct answer to force a nomination turn
		await current_comm.send_json_to({
			"action": GameAction.SUBMIT_ANSWER,
			"payload": {"answer": "yes"}
		})
		await current_comm.receive_json_from()
		await other_comm.receive_json_from()
		
		# Wait for auto-resolution to transition to nomination
		res_nom_phase = await current_comm.receive_json_from()
		await other_comm.receive_json_from()
		self.assertEqual(res_nom_phase["snapshot"]["current_status"], GameSession.Status.NOMINATION)
		
		# Wait for nomination timeout (100ms + some buffer)
		res_nom_timeout = await current_comm.receive_json_from()
		await other_comm.receive_json_from()

		self.assertEqual(res_nom_timeout["type"], "game_state_update")
		self.assertEqual(res_nom_timeout["action"], "nomination_timeout")
		self.assertEqual(res_nom_timeout["snapshot"]["current_status"], GameSession.Status.ANSWERING)
		self.assertIn(res_nom_timeout["snapshot"]["current_player"], [self.player.id, self.player2.id])
		
		await comm1.disconnect()
		await comm2.disconnect()

	async def _run_multi_player_timeout_test(self, num_players: int):
		# Create additional questions to support multiple turns
		for i in range(1, 4):
			q = await database_sync_to_async(Question.objects.create)(
				question_text=f"Question {i}?", correct_answer="yes"
			)
			await database_sync_to_async(SessionQuestion.objects.create)(
				session=self.session, question=q, order_index=i
			)

		# Set short timeouts to speed up the test
		await database_sync_to_async(
			lambda: GameSession.objects.filter(id=self.session.id).update(
				answer_time_limit_ms=150,
				nomination_time_limit_ms=150,
				evaluation_time_limit_ms=50
			)
		)()

		# Retrieve updated session
		session = await database_sync_to_async(GameSession.objects.get)(id=self.session.id)

		# We already have self.user/self.player and self.user2/self.player2.
		# Create the additional users and players as needed.
		users = [self.user, self.user2]
		cookies = [self.cookie, self.cookie2]
		players = [self.player, self.player2]

		for idx in range(3, num_players + 1):
			u = await database_sync_to_async(User.objects.create_user)(
				username=f"testuser{idx}",
				password="password",
				email=f"testuser{idx}@test.com"
			)
			p = await database_sync_to_async(SessionPlayer.objects.create)(
				session=session,
				user=u,
				display_name=f"Player {idx}",
				seat_number=idx
			)
			client = Client()
			await database_sync_to_async(client.force_login)(u)
			cookie = client.cookies.get('sessionid').value
			
			users.append(u)
			cookies.append(cookie)
			players.append(p)

		# Connect all players to WebSocket
		communicators = []
		for cookie in cookies:
			headers = [(b'cookie', f'sessionid={cookie}'.encode('ascii'))]
			comm = WebsocketCommunicator(
				self.application, f"/ws/game/{session.session_uuid}/", headers=headers
			)
			await comm.connect()
			# Consume connection state broadcast
			await comm.receive_json_from()
			communicators.append(comm)

		# Clear queue
		for comm in communicators:
			while not await comm.receive_nothing(timeout=0.01):
				await comm.receive_json_from()

		# 1. Start the game
		await communicators[0].send_json_to({"action": GameAction.START_GAME})
		
		# Receive start game event on all connections
		start_events = []
		for comm in communicators:
			evt = await comm.receive_json_from(timeout=2.0)
			self.assertEqual(evt["action"], GameAction.START_GAME)
			start_events.append(evt)

		# Get current player from snapshot
		current_player_id = start_events[0]["snapshot"]["current_player"]
		player_ids = [p.id for p in players]
		self.assertIn(current_player_id, player_ids)

		# Find index of current player
		curr_idx = player_ids.index(current_player_id)

		# 2. Test Answering Timeout
		eval_event = await communicators[0].receive_json_from(timeout=3.0)
		self.assertEqual(eval_event["action"], "evaluate_timeout")
		self.assertEqual(eval_event["snapshot"]["current_status"], GameSession.Status.EVALUATION)
		
		for i in range(1, len(communicators)):
			evt = await communicators[i].receive_json_from(timeout=2.0)
			self.assertEqual(evt["action"], "evaluate_timeout")

		# 3. Test Evaluation Finish
		next_turn_event = await communicators[0].receive_json_from(timeout=3.0)
		self.assertEqual(next_turn_event["action"], "handle_evaluation_finish")
		self.assertEqual(next_turn_event["snapshot"]["current_status"], GameSession.Status.ANSWERING)

		for i in range(1, len(communicators)):
			evt = await communicators[i].receive_json_from(timeout=2.0)
			self.assertEqual(evt["action"], "handle_evaluation_finish")

		# Get the new current player
		current_player_id = next_turn_event["snapshot"]["current_player"]
		self.assertIn(current_player_id, player_ids)
		curr_idx = player_ids.index(current_player_id)

		# 4. Test Nomination Timeout
		# Submit a correct answer to transition to EVALUATION and then to NOMINATION
		await communicators[curr_idx].send_json_to({
			"action": GameAction.SUBMIT_ANSWER,
			"payload": {"answer": "yes"}
		})
		
		for comm in communicators:
			evt = await comm.receive_json_from(timeout=2.0)
			self.assertEqual(evt["action"], GameAction.SUBMIT_ANSWER)
			self.assertEqual(evt["snapshot"]["current_status"], GameSession.Status.EVALUATION)

		nom_phase_event = await communicators[0].receive_json_from(timeout=3.0)
		self.assertEqual(nom_phase_event["snapshot"]["current_status"], GameSession.Status.NOMINATION)
		
		for i in range(1, len(communicators)):
			evt = await communicators[i].receive_json_from(timeout=2.0)
			self.assertEqual(evt["snapshot"]["current_status"], GameSession.Status.NOMINATION)

		# Let nomination phase time out
		nom_timeout_event = await communicators[0].receive_json_from(timeout=3.0)
		self.assertEqual(nom_timeout_event["action"], "nomination_timeout")
		self.assertEqual(nom_timeout_event["snapshot"]["current_status"], GameSession.Status.ANSWERING)

		for i in range(1, len(communicators)):
			evt = await communicators[i].receive_json_from(timeout=2.0)
			self.assertEqual(evt["action"], "nomination_timeout")

		new_player_id = nom_timeout_event["snapshot"]["current_player"]
		self.assertIn(new_player_id, player_ids)

		# Disconnect all
		for comm in communicators:
			await comm.disconnect()

	async def test_websocket_timeout_3_players(self):
		await self._run_multi_player_timeout_test(3)

	async def test_websocket_timeout_4_players(self):
		await self._run_multi_player_timeout_test(4)

	async def test_websocket_timeout_5_players(self):
		await self._run_multi_player_timeout_test(5)

	async def test_websocket_reconnection_state_sync(self):
		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1
		)
		await comm1.connect()
		await comm1.receive_json_from()
		
		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers2
		)
		await comm2.connect()
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		# Start game so disconnect doesn't delete player
		await comm1.send_json_to({"action": GameAction.START_GAME})
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		await comm1.disconnect()

		# Receive the disconnect broadcast on comm2
		disc_msg = await comm2.receive_json_from()
		self.assertEqual(disc_msg["type"], "game_state_update")
		self.assertEqual(disc_msg["action"], "disconnect")
		players = {p["id"]: p for p in disc_msg["snapshot"]["players"]}
		self.assertFalse(players[self.player.id]["is_online"])
		
		# Reconnect the same user and receive state immediately
		comm1_new = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1
		)
		connected, _ = await comm1_new.connect()
		self.assertTrue(connected)
		
		# comm1_new receives state sync on connect
		res = await comm1_new.receive_json_from()
		self.assertEqual(res["type"], "game_state_update")
		self.assertEqual(res["action"], "player_connected")
		players_new = {p["id"]: p for p in res["snapshot"]["players"]}
		self.assertTrue(players_new[self.player.id]["is_online"])

		# comm2 receives player_connected broadcast
		conn_msg = await comm2.receive_json_from()
		self.assertEqual(conn_msg["type"], "game_state_update")
		self.assertEqual(conn_msg["action"], "player_connected")
		players_conn = {p["id"]: p for p in conn_msg["snapshot"]["players"]}
		self.assertTrue(players_conn[self.player.id]["is_online"])
		
		await comm1_new.disconnect()
		await comm2.disconnect()

	async def test_non_host_cannot_start_game(self):
		headers = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		await communicator.receive_json_from()

		await communicator.send_json_to({
			"action": GameAction.START_GAME,
			"payload": {}
		})
		response = await communicator.receive_json_from()
		self.assertEqual(response["type"], "error")
		self.assertIn("Only the host can start the game", response["message"])
		await communicator.disconnect()

	async def test_submit_answer_out_of_turn(self):
		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1
		)
		await comm1.connect()
		await comm1.receive_json_from()
		
		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers2
		)
		await comm2.connect()
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		await comm1.send_json_to({"action": GameAction.START_GAME})
		res_start = await comm1.receive_json_from()
		await comm2.receive_json_from()
		
		current_player_id = res_start["snapshot"]["current_player"]
		other_comm = comm2 if current_player_id == self.player.id else comm1
		
		await other_comm.send_json_to({
			"action": GameAction.SUBMIT_ANSWER,
			"payload": {"answer": "yes"}
		})
		response = await other_comm.receive_json_from()
		self.assertEqual(response["type"], "error")
		self.assertIn("Only current player can submit answer", response["message"])
		
		await comm1.disconnect()
		await comm2.disconnect()

	async def test_nominate_out_of_turn(self):
		q2 = await database_sync_to_async(Question.objects.create)(
			question_text="Test2?", correct_answer="no"
		)
		await database_sync_to_async(SessionQuestion.objects.create)(
			session=self.session, question=q2, order_index=1
		)

		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1
		)
		await comm1.connect()
		await comm1.receive_json_from()
		
		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers2
		)
		await comm2.connect()
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		await comm1.send_json_to({"action": GameAction.START_GAME})
		res_start = await comm1.receive_json_from()
		await comm2.receive_json_from()
		
		current_player_id = res_start["snapshot"]["current_player"]
		current_comm = comm1 if current_player_id == self.player.id else comm2
		other_comm = comm2 if current_player_id == self.player.id else comm1
		other_player_id = self.player2.id if current_player_id == self.player.id else self.player.id
		
		await current_comm.send_json_to({
			"action": GameAction.SUBMIT_ANSWER,
			"payload": {"answer": "yes"}
		})
		await current_comm.receive_json_from()
		await other_comm.receive_json_from()
		
		# Receive the automated handle_evaluation_finish broadcast to transition to nomination
		await current_comm.receive_json_from()
		await other_comm.receive_json_from()
		
		await other_comm.send_json_to({
			"action": GameAction.NOMINATE_PLAYER,
			"payload": {"target_player_id": other_player_id}
		})
		response = await other_comm.receive_json_from()
		self.assertEqual(response["type"], "error")
		self.assertIn("Only last correct player can nominate", response["message"])
		
		await comm1.disconnect()
		await comm2.disconnect()

	async def test_nominate_invalid_player(self):
		q2 = await database_sync_to_async(Question.objects.create)(
			question_text="Test2?", correct_answer="no"
		)
		await database_sync_to_async(SessionQuestion.objects.create)(
			session=self.session, question=q2, order_index=1
		)

		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1
		)
		await comm1.connect()
		await comm1.receive_json_from()
		
		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers2
		)
		await comm2.connect()
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		await comm1.send_json_to({"action": GameAction.START_GAME})
		res_start = await comm1.receive_json_from()
		await comm2.receive_json_from()
		
		current_player_id = res_start["snapshot"]["current_player"]
		current_comm = comm1 if current_player_id == self.player.id else comm2
		other_comm = comm2 if current_player_id == self.player.id else comm1
		
		await current_comm.send_json_to({
			"action": GameAction.SUBMIT_ANSWER,
			"payload": {"answer": "yes"}
		})
		await current_comm.receive_json_from()
		await other_comm.receive_json_from()
		
		# Receive the automated handle_evaluation_finish broadcast to transition to nomination
		await current_comm.receive_json_from()
		await other_comm.receive_json_from()
		
		await current_comm.send_json_to({
			"action": GameAction.NOMINATE_PLAYER,
			"payload": {"target_player_id": 9999}
		})
		response = await current_comm.receive_json_from()
		self.assertEqual(response["type"], "error")
		self.assertIn("Player does not belong to this session", response["message"])
		
		await comm1.disconnect()
		await comm2.disconnect()

	async def test_websocket_disconnect_in_game_over(self):
		self.session.current_status = GameSession.Status.GAME_OVER
		await database_sync_to_async(self.session.save)()

		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		await communicator.receive_json_from()

		await communicator.disconnect()

		session_exists = await database_sync_to_async(
			GameSession.objects.filter(id=self.session.id).exists
		)()
		self.assertTrue(session_exists)

	async def test_host_disconnect_transfers_host(self):
		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1
		)
		await comm1.connect()
		await comm1.receive_json_from()
		
		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers2
		)
		await comm2.connect()
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		await comm1.disconnect()

		response = await comm2.receive_json_from()
		self.assertEqual(response["type"], "game_state_update")
		self.assertEqual(response["action"], GameAction.DISCONNECT)

		# Host should NOT be transferred immediately because it's graceful
		host_player_id = await database_sync_to_async(
			lambda: GameSession.objects.get(id=self.session.id).host_player_id
		)()
		self.assertEqual(host_player_id, self.player.id)

		# Fast forward disconnected_at past the grace period
		from django.utils import timezone
		from datetime import timedelta
		from django.conf import settings
		grace_limit = timezone.now() - timedelta(seconds=settings.DISCONNECT_GRACE_PERIOD_S + 1)
		await database_sync_to_async(
			lambda: SessionPlayer.objects.filter(id=self.player.id).update(disconnected_at=grace_limit)
		)()

		# Expire players (simulating another event/sync)
		from game.services.game_flow.game_action_handler import GameActionHandler
		handler = GameActionHandler()
		await database_sync_to_async(handler.sync_game_disconnections)(self.session.id)

		# Host should now be transferred
		host_player_id = await database_sync_to_async(
			lambda: GameSession.objects.get(id=self.session.id).host_player_id
		)()
		self.assertEqual(host_player_id, self.player2.id)
		
		await comm2.disconnect()

	async def test_player_explicit_leave_game_removes_immediately(self):
		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1
		)
		await comm1.connect()
		await comm1.receive_json_from()
		
		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers2
		)
		await comm2.connect()
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		# comm1 (host) explicitly leaves
		await comm1.send_json_to({"action": GameAction.LEAVE_GAME})
		
		# comm2 receives update immediately
		response = await comm2.receive_json_from()
		self.assertEqual(response["type"], "game_state_update")
		self.assertEqual(response["action"], GameAction.LEAVE_GAME)

		# Host should be transferred immediately
		host_player_id = await database_sync_to_async(
			lambda: GameSession.objects.get(id=self.session.id).host_player_id
		)()
		self.assertEqual(host_player_id, self.player2.id)

		# Player 1 should be deleted immediately (not in players snapshot list)
		players_in_snapshot = [p["id"] for p in response["snapshot"]["players"]]
		self.assertNotIn(self.player.id, players_in_snapshot)
		
		await comm1.disconnect()
		await comm2.disconnect()

	async def test_websocket_full_game_to_game_over(self):
		q2 = await database_sync_to_async(Question.objects.create)(
			question_text="Test2?", correct_answer="no"
		)
		await database_sync_to_async(SessionQuestion.objects.create)(
			session=self.session, question=q2, order_index=1
		)

		self.player.lives = 1
		self.player2.lives = 1
		await database_sync_to_async(self.player.save)()
		await database_sync_to_async(self.player2.save)()

		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1
		)
		await comm1.connect()
		await comm1.receive_json_from()
		
		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers2
		)
		await comm2.connect()
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		await comm1.send_json_to({"action": GameAction.START_GAME})
		res_start = await comm1.receive_json_from()
		await comm2.receive_json_from()
		
		current_player_id = res_start["snapshot"]["current_player"]
		current_comm = comm1 if current_player_id == self.player.id else comm2
		other_comm = comm2 if current_player_id == self.player.id else comm1
		other_player_id = self.player2.id if current_player_id == self.player.id else self.player.id
		
		await current_comm.send_json_to({
			"action": GameAction.SUBMIT_ANSWER,
			"payload": {"answer": "yes"}
		})
		res_eval = await current_comm.receive_json_from()
		await other_comm.receive_json_from()
		self.assertEqual(res_eval["snapshot"]["current_status"], GameSession.Status.EVALUATION)

		# Wait for auto-resolution to transition to nomination
		res_nom_phase = await current_comm.receive_json_from()
		await other_comm.receive_json_from()
		self.assertEqual(res_nom_phase["snapshot"]["current_status"], GameSession.Status.NOMINATION)
		
		await current_comm.send_json_to({
			"action": GameAction.NOMINATE_PLAYER,
			"payload": {"target_player_id": other_player_id}
		})
		res_nom = await current_comm.receive_json_from()
		await other_comm.receive_json_from()
		
		self.assertEqual(res_nom["snapshot"]["current_status"], GameSession.Status.ANSWERING)
		self.assertEqual(res_nom["snapshot"]["current_player"], other_player_id)
		
		await other_comm.send_json_to({
			"action": GameAction.SUBMIT_ANSWER,
			"payload": {"answer": "wrong"}
		})
		res_eval_wrong = await other_comm.receive_json_from()
		await current_comm.receive_json_from()
		self.assertEqual(res_eval_wrong["snapshot"]["current_status"], GameSession.Status.EVALUATION)

		# Wait for auto-resolution to transition to game over
		res_game_over = await other_comm.receive_json_from()
		await current_comm.receive_json_from()
		
		self.assertEqual(res_game_over["snapshot"]["current_status"], GameSession.Status.GAME_OVER)
		self.assertEqual(res_game_over["snapshot"]["winner"], current_player_id)
		
		await comm1.disconnect()
		await comm2.disconnect()

	async def test_connect_to_nonexistent_session(self):
		import uuid
		fake_uuid = uuid.uuid4()
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{fake_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertFalse(connected)

	async def test_receive_unknown_action(self):
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		await communicator.receive_json_from()

		await communicator.send_json_to({"action": "NONEXISTENT_ACTION", "payload": {}})
		response = await communicator.receive_json_from()
		self.assertEqual(response["type"], "error")
		await communicator.disconnect()

	async def test_nomination_freeze_bug_reproduction(self):
		import asyncio
		from django.utils import timezone
		from datetime import timedelta
		from django.conf import settings

		q2 = await database_sync_to_async(Question.objects.create)(question_text="Second?", correct_answer="yes")
		await database_sync_to_async(SessionQuestion.objects.create)(session=self.session, question=q2, order_index=1)
		q3 = await database_sync_to_async(Question.objects.create)(question_text="Third?", correct_answer="yes")
		await database_sync_to_async(SessionQuestion.objects.create)(session=self.session, question=q3, order_index=2)

		self.session.answer_time_limit_ms = 100
		self.session.nomination_time_limit_ms = 100
		self.session.evaluation_time_limit_ms = 100
		await database_sync_to_async(self.session.save)()

		user3 = await database_sync_to_async(User.objects.create_user)(
			username="testuser3", password="password", email="testuser3@test.com"
		)
		player3 = await database_sync_to_async(SessionPlayer.objects.create)(
			session=self.session, user=user3, display_name="Player 3", seat_number=3
		)

		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1)
		await comm1.connect()
		await comm1.receive_json_from()

		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers2)
		await comm2.connect()
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		client3 = Client()
		await database_sync_to_async(client3.force_login)(user3)
		cookie3 = client3.cookies.get('sessionid').value
		headers3 = [(b'cookie', f'sessionid={cookie3}'.encode('ascii'))]
		comm3 = WebsocketCommunicator(self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers3)
		await comm3.connect()
		await comm1.receive_json_from()
		await comm2.receive_json_from()
		await comm3.receive_json_from()

		await comm1.send_json_to({"action": GameAction.START_GAME})
		res_start = await comm1.receive_json_from()
		await comm2.receive_json_from()
		await comm3.receive_json_from()

		current_player_id = res_start["snapshot"]["current_player"]
		current_comm = comm1 if current_player_id == self.player.id else (comm2 if current_player_id == self.player2.id else comm3)

		await current_comm.send_json_to({
			"action": GameAction.SUBMIT_ANSWER,
			"payload": {"answer": "yes"}
		})
		await comm1.receive_json_from()
		await comm2.receive_json_from()
		await comm3.receive_json_from()

		await asyncio.sleep(0.2)
		
		session = await database_sync_to_async(lambda: GameSession.objects.get(id=self.session.id))()
		self.assertEqual(session.current_status, GameSession.Status.NOMINATION)

		nominator_id = session.last_correct_player_id
		nominator_comm = comm1 if nominator_id == self.player.id else (comm2 if nominator_id == self.player2.id else comm3)
		nominator_user = self.user if nominator_id == self.player.id else (self.user2 if nominator_id == self.player2.id else user3)

		await nominator_comm.disconnect()

		def _expire_nominator():
			n = SessionPlayer.objects.get(session_id=self.session.id, user=nominator_user)
			n.disconnected_at = timezone.now() - timedelta(seconds=settings.DISCONNECT_GRACE_PERIOD_S + 1)
			n.save()
		await database_sync_to_async(_expire_nominator)()

		other_comm = comm2 if nominator_comm != comm2 else comm3
		await other_comm.disconnect()

		await asyncio.sleep(0.5)

		session = await database_sync_to_async(lambda: GameSession.objects.get(id=self.session.id))()
		self.assertEqual(session.current_status, GameSession.Status.EVALUATION)

		if nominator_comm != comm1 and other_comm != comm1:
			await comm1.disconnect()
		if nominator_comm != comm2 and other_comm != comm2:
			await comm2.disconnect()
		if nominator_comm != comm3 and other_comm != comm3:
			await comm3.disconnect()
