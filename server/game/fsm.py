from statemachine import StateMachine, State

class GameStateMachine(StateMachine):
	lobby = State("Lobby", initial=True)

	opening_phase_answering = State("Opening Answering")
	opening_phase_evaluation = State("Opening Evaluation")

	player_nomination = State("Player Nomination")
	nominated_answering = State("Nominated Answering")
	nomination_evaluation = State("Nomination Evaluation")

	game_over = State("Game Over", final=True)

	# --- Transitions (Events) ---
	start_game = lobby.to(opening_phase_answering)

	answer_opening = opening_phase_answering.to(opening_phase_evaluation)
	
	evaluate_opening = (
		opening_phase_evaluation.to(game_over, cond="is_game_over") |
		opening_phase_evaluation.to(player_nomination, cond="is_correct") |
		opening_phase_evaluation.to(opening_phase_answering, on="on_opening_wrong")
	)

	nominate_player = player_nomination.to(nominated_answering)
	
	answer_nominated = nominated_answering.to(nomination_evaluation)

	evaluate_nomination = (
		nomination_evaluation.to(game_over, cond="is_game_over") |
		nomination_evaluation.to(player_nomination, cond="is_nominator_alive") |
		nomination_evaluation.to(player_nomination, on="on_nominator_eliminated") 
	)

	# --- Guards ---
	def is_correct(self):
		return self.model.player_answer_correct is True

	def is_game_over(self):
		alive_players = sum(1 for p in self.model.players.values() if p.lives > 0)
		questions_exhausted = self.model.question_asked_count >= len(self.model.session_questions_ids)
		return alive_players <= 1 or questions_exhausted
	
	def is_nominator_alive(self):
		if self.model.nominator_id is None:
			return False
		return self.model.players[self.model.nominator_id].lives > 0

	# --- Helper Callbacks ---
	def _assign_next_question(self):
		if self.model.question_asked_count < len(self.model.session_questions_ids):
			self.model.current_question_id = self.model.session_questions_ids[self.model.question_asked_count]
			self.model.question_asked_count += 1

	def _get_next_alive_player_id(self, current_id: int) -> int:
		if not any(p.lives > 0 for p in self.model.players.values()):
			return current_id
		max_id = max(self.model.players.keys())
		next_id = current_id + 1
		while True:
			if next_id > max_id:
				next_id = 1
			if self.model.players[next_id].lives > 0:
				return next_id
			next_id += 1

	# --- Callbacks ---
	def on_start_game(self, starting_player_id: int = 1):
		self.model.current_player_id = starting_player_id
		self._assign_next_question()

	def on_answer_opening(self, answer: str | None, is_correct: bool):
		self.model.player_answer = answer
		self.model.player_answer_correct = is_correct
		if is_correct:
			self.model.players[self.model.current_player_id].points += 10
			self.model.nominator_id = self.model.current_player_id
		else:
			self.model.players[self.model.current_player_id].lives -= 1

	def on_opening_wrong(self):
		self.model.current_player_id = self._get_next_alive_player_id(self.model.current_player_id)
		self._assign_next_question()

	def on_nominate_player(self, target_player_id: int):
		self.model.current_player_id = target_player_id
		self._assign_next_question()

	def on_answer_nominated(self, answer: str | None, is_correct: bool):
		self.model.player_answer = answer
		self.model.player_answer_correct = is_correct
		if is_correct:
			if self.model.current_player_id == self.model.nominator_id:
				self.model.players[self.model.current_player_id].points += 20
			else:
				self.model.players[self.model.current_player_id].points += 10
			self.model.nominator_id = self.model.current_player_id
		else:
			self.model.players[self.model.current_player_id].lives -= 1

	def on_nominator_eliminated(self):
		self.model.nominator_id = self._get_next_alive_player_id(self.model.current_player_id)
		self.model.current_player_id = None