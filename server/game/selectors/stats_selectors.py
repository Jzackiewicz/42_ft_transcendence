from django.db.models import Avg, Sum, Max, Count, Q
from account.selectors import user_get_by_id
from game.models import GameSession, SessionPlayer, AnswerAttempt


# Database queries

def _query_player_stats(user) -> dict:
    completed_sessions = SessionPlayer.objects.filter(
        user=user,
        session__current_status=GameSession.Status.GAME_OVER
    )
    return completed_sessions.aggregate(
        games_played=Count('id'),
        total_points=Sum('points'),
        avg_score=Avg('points'),
        highest_score=Max('points')
    )


def _query_attempt_stats(user) -> dict:
    completed_attempts = AnswerAttempt.objects.filter(
        player__user=user,
        session__current_status=GameSession.Status.GAME_OVER
    )
    return completed_attempts.aggregate(
        total=Count('id'),
        correct=Count('id', filter=Q(is_correct=True)),
        avg_time_ms=Avg(
            'answer_time_ms',
            filter=Q(is_timeout=False, evaluation_status=AnswerAttempt.EvaluationStatus.EVALUATED)
        )
    )


def _query_wins(user) -> int:
    completed_wins = GameSession.objects.filter(
        current_status=GameSession.Status.GAME_OVER,
        winner__user=user
    )
    return completed_wins.count()


# Stats preparation functions

def _get_games_played(player_stats: dict) -> int:
    return player_stats['games_played'] or 0


def _get_wins(wins_count: int) -> int:
    return wins_count


def _get_win_rate(*, wins: int, games_played: int) -> float:
    if games_played == 0:
        return 0.0
    return round((wins / games_played) * 100.0, 1)


def _get_total_points(player_stats: dict) -> int:
    return player_stats['total_points'] or 0


def _get_avg_score(player_stats: dict) -> float:
    avg = player_stats['avg_score'] or 0.0
    return round(avg, 1)


def _get_highest_score(player_stats: dict) -> int:
    return player_stats['highest_score'] or 0


def _get_correct_rate(attempt_stats: dict) -> float:
    total = attempt_stats['total'] or 0
    if total == 0:
        return 0.0
    correct = attempt_stats['correct'] or 0
    return round((correct / total) * 100.0, 1)


def _get_avg_answer_time_seconds(attempt_stats: dict) -> float:
    avg_ms = attempt_stats['avg_time_ms'] or 0.0
    return round(avg_ms / 1000.0, 2)


# Main Selector

def get_user_game_stats(*, user_id: int) -> dict:
    user = user_get_by_id(user_id=user_id)

    player_stats = _query_player_stats(user)
    attempt_stats = _query_attempt_stats(user)

    games_played = _get_games_played(player_stats)
    wins = _query_wins(user)

    return {
        "games_played": games_played,
        "wins": wins,
        "win_rate": _get_win_rate(wins=wins, games_played=games_played),
        "avg_score": _get_avg_score(player_stats),
        "total_points": _get_total_points(player_stats),
        "highest_score": _get_highest_score(player_stats),
        "correct_rate": _get_correct_rate(attempt_stats),
        "avg_answer_time_seconds": _get_avg_answer_time_seconds(attempt_stats),
    }
