from statemachine import StateMachine, State
from dataclasses import dataclass


# @dataclass
# class Player:
# 	id: int
# 	name: str
# 	lives: int = 3
# 	points: int = 0

# @dataclass
# class GameSession:
# 	players: dict[int, Player]
# 	session_questions_ids: list[int]
# 	current_status: str = "Lobby"
# 	current_player_id: int | None = None
# 	current_question_id: int | None = None
# 	question_asked_count: int = 0

# 	def __post_init__(self):
# 		self.fsm = GameStateMachine(model=self, state_field="current_status")

class GameStateMachine(StateMachine):
	lobby = State("Lobby", value="Lobby", initial=True)

	opening_phase_answering = State("Opening Answering", value="Opening Answering")
	opening_phase_evaluation = State("Opening Evaluation", value="Opening Evaluation")

	player_nomination = State("Player Nomination", value="Player Nomination")
	nominated_answering = State("Nominated Answering", value="Nominated Answering")
	nomination_evaluation = State("Nomination Evaluation", value="Nomination Evaluation")

	game_over = State("Game Over", value="Game Over", final=True)

	# --- Transitions ---
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
		alive_players = self.model.session_players.filter(lives__gt=0).count()
		questions_exhausted = self.model.question_asked_count >= len(self.model.session_questions_ids)
		return alive_players <= 1 or questions_exhausted
	
	def is_nominator_alive(self):
		if self.model.nominator_id is None:
			return False
		nominator = self.model.session_players.filter(player_id=self.model.nominator_id).first()
		return nominator is not None and nominator.lives > 0

	# --- Helper Callbacks ---
	def _assign_next_question(self):
		if self.model.question_asked_count < len(self.model.session_questions_ids):
			self.model.current_question_id = self.model.session_questions_ids[self.model.question_asked_count]
			self.model.question_asked_count += 1

	def _get_next_alive_player_id(self, current_id: int) -> int:
		alive_ids = list(self.model.session_players.filter(lives__gt=0).values_list('player_id', flat=True))
		
		if not alive_ids:
			return current_id
		alive_ids.sort()
		for player_id in alive_ids:
			if player_id > current_id:
				return player_id
		return alive_ids[0]

	# --- Callbacks ---
	def on_start_game(self, starting_player_id: int = 1):
		self.model.current_player_id = starting_player_id
		self._assign_next_question()

	def on_answer_opening(self, answer: str | None, is_correct: bool):
		self.model.player_answer = answer
		self.model.player_answer_correct = is_correct

		player = self.model.session_players.get(player_id=self.model.current_player_id)
		if is_correct:
			player.points += 10
			self.model.nominator_id = self.model.current_player_id
		else:
			player.lives -= 1
		player.save()

	def on_opening_wrong(self):
		self.model.current_player_id = self._get_next_alive_player_id(self.model.current_player_id)
		self._assign_next_question()

	def on_nominate_player(self, target_player_id: int):
		self.model.current_player_id = target_player_id
		self._assign_next_question()

	def on_answer_nominated(self, answer: str | None, is_correct: bool):
		self.model.player_answer = answer
		self.model.player_answer_correct = is_correct
		
		player = self.model.session_players.get(player_id=self.model.current_player_id)
		if is_correct:
			if self.model.current_player_id == self.model.nominator_id:
				player.points += 20
			else:
				player.points += 10
			self.model.nominator_id = self.model.current_player_id
		else:
			player.lives -= 1
		player.save()

	def on_nominator_eliminated(self):
		next_alive_player_id = self._get_next_alive_player_id(self.model.current_player_id)
		self.model.nominator_id = next_alive_player_id
		self.model.current_player_id = next_alive_player_id