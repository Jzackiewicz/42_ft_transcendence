from statemachine import StateMachine, State


class GameStateMachine(StateMachine):
	lobby = State("Lobby", value="Lobby", initial=True)
	answering = State("Answering", value="Answering")
	evaluation = State("Evaluation", value="Evaluation")
	nomination = State("Nomination", value="Nomination")
	game_over = State("Game Over", value="Game Over", final=True)

	# Transitions
	start_game = lobby.to(answering)

	submit_answer = answering.to(evaluation)

	mark_correct = (
		evaluation.to(game_over, cond="is_game_over") |
		evaluation.to(nomination)
	)

	mark_wrong = (
		evaluation.to(game_over, cond="is_game_over") |
		evaluation.to(nomination, cond="has_alive_last_correct_player") |
		evaluation.to(answering, on="on_no_last_correct_player_fallback")
	)

	nominate_player = nomination.to(answering)

	# Guards
	def has_alive_last_correct_player(self):
		if self.model.last_correct_player_id is None:
			return False
		player = self.model.session_players.filter(
			player_id=self.model.last_correct_player_id
		).first()
		return player is not None and player.lives > 0

	def is_game_over(self):
		alive_players = self.model.session_players.filter(lives__gt=0).count()
		questions_exhausted = (
			self.model.question_asked_count >= len(self.model.session_questions_ids)
		)
		return alive_players <= 1 or questions_exhausted

	# Helper methods
	def _assign_next_question(self):
		if self.model.question_asked_count < len(self.model.session_questions_ids):
			self.model.current_question_id = self.model.session_questions_ids[
				self.model.question_asked_count
			]
			self.model.question_asked_count += 1
		else:
			self.model.current_question_id = None

	def _get_next_alive_player_id(self, current_id: int) -> int:
		alive_ids = list(
			self.model.session_players
			.filter(lives__gt=0)
			.values_list("player_id", flat=True)
		)

		if not alive_ids:
			return current_id

		alive_ids.sort()

		for player_id in alive_ids:
			if player_id > current_id:
				return player_id
		return alive_ids[0]

	def _get_current_player(self):
		return self.model.session_players.get(player_id=self.model.current_player_id)

	# Callbacks
	def on_start_game(self, starting_player_id: int = 1):
		self.model.current_player_id = starting_player_id
		self.model.last_correct_player_id = None
		self.model.last_nominated_player_id = None
		self.model.player_answer = None
		self.model.player_answer_correct = None
		self.model.player_answer_is_timeout = False
		self._assign_next_question()

	def on_submit_answer(self, answer: str | None, is_timeout: bool = False):
		self.model.player_answer = answer
		self.model.player_answer_correct = None
		self.model.player_answer_is_timeout = is_timeout

	def on_mark_correct(self):
		player = self._get_current_player()

		if self.model.current_player_id == self.model.last_nominated_player_id:
			player.points += 20
		else:
			player.points += 10

		self.model.player_answer_correct = True
		self.model.last_correct_player_id = self.model.current_player_id

		player.save()

	def on_mark_wrong(self):
		player = self._get_current_player()

		player.lives -= 1
		self.model.player_answer_correct = False

		player.save()

	def on_no_last_correct_player_fallback(self):
		self.model.current_player_id = self._get_next_alive_player_id(self.model.current_player_id)
		self._assign_next_question()

	def on_nominate_player(self, target_player_id: int):
		target = self.model.session_players.get(player_id=target_player_id)
		if target.lives <= 0:
			raise ValueError("Cannot nominate a dead player")

		self.model.last_nominated_player_id = target_player_id
		self.model.current_player_id = target_player_id
		self._assign_next_question()