from statemachine import StateMachine, State
from dataclasses import dataclass


@dataclass
class Player:
	id: int
	name: str
	lives: int = 3
	points: int = 0

@dataclass
class Question:
	id: int
	text: str
	correct_answer: str

@dataclass
class GameSession:
	players: dict[int, Player]
	session_questions_ids: list[int]
	current_status: str = "Lobby"
	current_player_id: int | None = None
	current_question_id: int | None = None
	question_asked_count: int = 0

	def __post_init__(self):
		self.fsm = GameStateMachine(model=self, state_field="current_status")


class GameStateMachine(StateMachine):
	lobby = State("Lobby", initial=True)
	player_nomination = State("Player Nomination")
	player_answering = State("Player Answering")
	answer_evaluation = State("Answer Evaluation")
	game_over = State("Game Over", final=True)

	start_game = lobby.to(player_nomination)

	player_nominated = player_nomination.to(player_answering)
	nomination_timeout = player_nomination.to(player_answering)

	target_player_answered = player_answering.to(answer_evaluation)
	answer_timeout = player_answering.to(answer_evaluation)

	next_round = answer_evaluation.to(player_nomination)
	finish_game = answer_evaluation.to(game_over, cond="game_over_condition")

	def on_start_game(self, first_player_id: int, question_id: int):
		self.current_player_id = first_player_id
		self.current_question_id = question_id
		self.question_asked_count += 1
		print(f"Starting game, first player is: {self.current_player_id}, first question is: {self.current_question_id}")

	def on_player_nominated(self, player_id: int, question_id: int):
		self.current_player_id = player_id
		self.current_question_id = question_id
		print(f"Player {player_id} is nominated, question is: {question_id}")

	def on_exit_player_nomination(self):
		print("Exiting Player Nomination state")

	
	# Conditions
	def is_game_over(self):
		alive_players = [p for p in self.players.values() if p.lives > 0]
		return len(alive_players) <= 1 or self.question_asked_count >= len(self.session_questions_ids)