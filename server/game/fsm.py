from statemachine import StateMachine, State


class GameStateMachine(StateMachine):
	lobby = State("Lobby", value="lobby", initial=True)
	answering = State("Answering", value="answering")
	evaluation = State("Evaluation", value="evaluation")
	nomination = State("Nomination", value="nomination")
	game_over = State("Game Over", value="game_over", final=True)

	# Transitions
	start_game = lobby.to(answering)
	submit_answer = answering.to(evaluation)

	mark_correct = evaluation.to(evaluation)
	mark_wrong = evaluation.to(evaluation)

	resolve_evaluation = (
		evaluation.to(game_over, cond="is_game_over") |
		evaluation.to(nomination, cond="has_alive_last_correct_player") |
		evaluation.to(answering, on="on_no_last_correct_player_fallback")
	)

	nominate_player = nomination.to(answering)

	# Guards
	def has_alive_last_correct_player(self):
		if self.model.last_correct_player_id is None:
			return False

		return self.model.session_players.filter(
			id=self.model.last_correct_player_id,
			lives__gt=0,
		).exists()

	def is_game_over(self):
		alive_players = self.model.session_players.filter(lives__gt=0).count()
		questions_exhausted = (
			self.model.question_asked_count >= self.model.session_questions.count()
		)
		return alive_players <= 1 or questions_exhausted

	# Helpers
	def _assign_next_question(self):
		next_question = self.model.session_questions.filter(
			order_index=self.model.question_asked_count
		).first()

		if next_question is not None:
			self.model.current_question = next_question
			self.model.question_asked_count += 1
		else:
			self.model.current_question = None

	def _get_next_alive_player(self, current_player):
		alive_players = list(
			self.model.session_players.filter(lives__gt=0).order_by("seat_number")
		)

		if not alive_players:
			return current_player

		for player in alive_players:
			if player.seat_number > current_player.seat_number:
				return player

		return alive_players[0]
	
	# Callbacks
	def on_start_game(self, starting_player_id: int):
		starting_player = self.model.session_players.get(id=starting_player_id)

		self.model.current_player = starting_player
		self.model.last_correct_player = None
		self.model.last_nominated_player = None
		self._assign_next_question()

	def on_mark_correct(self):
		attempt = self.model.current_attempt
		if attempt is None:
			raise ValueError("No pending attempt to mark as correct")

		player = attempt.player

		if self.model.last_nominated_player_id == player.id:
			player.points += 20
		else:
			player.points += 10

		player.answered_count += 1
		player.save()
		self.model.last_correct_player = player

	def on_mark_wrong(self):
		attempt = self.model.current_attempt
		if attempt is None:
			raise ValueError("No pending attempt to mark as correct")

		player = attempt.player

		if player.lives > 0:
			player.lives -= 1
		player.answered_count += 1
		player.save()

	def on_no_last_correct_player_fallback(self):
		next_player = self._get_next_alive_player(self.model.current_player)
		self.model.current_player = next_player
		self._assign_next_question()

	def on_nominate_player(self, target_player_id: int):
		target = self.model.session_players.get(id=target_player_id)
		if target.lives <= 0:
			raise ValueError("Cannot nominate a dead player")

		self.model.last_nominated_player = target
		self.model.current_player = target
		self._assign_next_question()