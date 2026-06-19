import { Player } from '../../useGamePage';
import { Button } from '../../../../components/Button/Button';
import './GameOverView.css';

interface GameOverViewProps {
    winnerId: number | null;
    players: Player[];
    onReturnToHome: () => void;
}

export function GameOverView({ winnerId, players, onReturnToHome }: GameOverViewProps) {
    const sortedLeaderboard = [...players].sort((a, b) => {
        // 0. The official winner always comes first
        if (winnerId !== null) {
            if (a.id === winnerId) return -1;
            if (b.id === winnerId) return 1;
        }

        // 1. Survival status: alive players (is_alive = true) first
        if (b.is_alive !== a.is_alive) {
            return b.is_alive ? 1 : -1;
        }

        // 2. points DESC (highest points first)
        if (b.points !== a.points) {
            return b.points - a.points;
        }

        // 3. answered_count DESC (most answered questions first)
        if (b.answered_count !== a.answered_count) {
            return b.answered_count - a.answered_count;
        }

        // 4. total_answer_time_ms ASC (fastest total response time first)
        const aTime = a.total_answer_time_ms ?? 0;
        const bTime = b.total_answer_time_ms ?? 0;
        if (aTime !== bTime) {
            return aTime - bTime;
        }

        // 5. seat_number ASC (lowest seat number first)
        return a.seat_number - b.seat_number;
    });

    // Render lives as visual hearts
    const renderHearts = (lives: number) =>
        Array.from({ length: 3 })
            .map((_, i) => (i < lives ? '❤️' : '🖤'))
            .join('');

    return (
        <div className="game-over-container">

            <table className="game-over-table">
                <thead className="game-over-thead">
                    <tr>
                        <th>Rank</th>
                        <th>Player</th>
                        <th>Points</th>
                        <th>Lives</th>
                        <th>Answers</th>
                    </tr>
                </thead>
                <tbody>
                    {sortedLeaderboard.map((player, idx) => {
                        const isWinner = player.id === winnerId;
                        const rowClasses = [
                            'game-over-row',
                            isWinner ? 'winner-row' : '',
                            !player.is_alive ? 'eliminated-row' : ''
                        ].filter(Boolean).join(' ');

                        return (
                            <tr key={player.id} className={rowClasses}>
                                <td className="game-over-rank">
                                    #{idx + 1}
                                </td>
                                <td className="game-over-player-cell">
                                    <div className="game-over-player-info">
                                        {player.avatar ? (
                                            <img
                                                src={player.avatar}
                                                alt={`${player.display_name}'s avatar`}
                                                className="game-over-avatar"
                                            />
                                        ) : (
                                            <span className="game-over-avatar-placeholder">👤</span>
                                        )}
                                        <span className="game-over-player-name">
                                            {player.display_name}
                                        </span>
                                    </div>
                                </td>
                                <td className="game-over-points">
                                    {player.points}
                                </td>
                                <td className="game-over-lives">
                                    {renderHearts(player.lives)}
                                </td>
                                <td className="game-over-answers">
                                    {player.answered_count}
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>

            {/* ── Actions ────────────────────────────────────────── */}
            <div className="game-over-actions">
                <Button onClick={onReturnToHome}>
                    Return to Home
                </Button>
            </div>

        </div>
    );
}
