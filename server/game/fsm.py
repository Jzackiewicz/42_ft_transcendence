from statemachine import StateMachine, State
from dataclasses import dataclass
import random


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
	time_expired = player_answering.to(answer_evaluation)
	next_round = answer_evaluation.to(player_nomination)
	finish_game = answer_evaluation.to(game_over, cond="game_over_condition")

	def on_start_game(self):
		self.model.current_player_id = random.choice(self.model.players).id
	
	def on_exit_player_nomination(self):
		print("Exiting Player Nomination state")


	def game_over_condition(self):
		return self.players_count <= 1 #or self.left_questions_count == 0
