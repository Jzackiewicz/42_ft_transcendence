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

	resolve_evaluation = (
		evaluation.to(game_over, cond="is_game_over") |
		evaluation.to(nomination, cond="has_last_correct_player_alive") |
		evaluation.to(answering)
	)

	nominate_player = nomination.to(answering)

	# Guards
	def has_last_correct_player_alive(self):
		return self.model.has_last_correct_player_alive()

	def is_game_over(self):
		return self.model.is_game_over()