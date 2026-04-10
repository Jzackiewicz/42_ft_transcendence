from statemachine import StateMachine, State


class GameStateMachine(StateMachine):
	lobby = State("Lobby", initial=True)
	player_nomination = State("Player Nomination")
	collecting_answers = State("Collecting Answers")
	answer_evaluation = State("Answers Evaluation")
	game_over = State("Game Over", final=True)

	start_game = lobby.to(player_nomination)
	player_nominated = player_nomination.to(collecting_answers)
	non_target_player_answered = collecting_answers.to(collecting_answers)
	target_player_answered = collecting_answers.to(answer_evaluation)
	time_expired = collecting_answers.to(answer_evaluation)
	next_round = answer_evaluation.to(player_nomination, cond="more_than_one_player_remaining")
	finish_game = answer_evaluation.to(game_over, cond="last_player_remaining")

	def __init__(self, players_count: int = 2):
		self.players_count = players_count
		super().__init__()

	def more_than_one_player_remaining(self):
		return self.players_count > 1

	def last_player_remaining(self):
		return self.players_count <= 1
