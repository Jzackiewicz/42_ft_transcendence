from game.models import GameSession, SessionPlayer


def get_random_alive_player(session: GameSession) -> SessionPlayer | None:
	return session.session_players.filter(lives__gt=0).order_by("?").first()


def get_next_alive_player(
	session: GameSession,
	current_player: SessionPlayer,
) -> SessionPlayer:
	alive_players = list(
		session.session_players.filter(lives__gt=0).order_by("seat_number")
	)

	if not alive_players:
		return current_player

	for player in alive_players:
		if player.seat_number > current_player.seat_number:
			return player

	return alive_players[0]

def get_new_host_player(session: GameSession) -> SessionPlayer | None:
	return session.session_players.filter(seat_number__isnull=False).order_by('id').first()