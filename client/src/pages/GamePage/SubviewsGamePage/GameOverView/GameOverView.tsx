import React from 'react';
import { Player } from '../../useGamePage';
import './GameOverView.css';

interface GameOverViewProps {
    winnerId: number | null;
    winnerName: string;
    endReason: string;
    players: Player[];
    onReturnToHome: () => void;
}

export function GameOverView({ winnerId, winnerName, endReason, players, onReturnToHome }: GameOverViewProps) {
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

    return (
        <div className="game-over-container">
            <h2 className="game-over-title">Game Over!</h2>

            <div className="game-over-winner-card">
                <div className="game-over-winner-name">
                    🏆 Winner: {winnerName || 'No winner (Draw)'}
                </div>
                <div className="game-over-reason">
                    <strong>Reason:</strong> {endReason || 'Game completed.'}
                </div>
            </div>

            <h3>Final Standings</h3>
            <table className="game-over-table">
                <thead>
                    <tr className="game-over-table-header">
                        <th className="game-over-th-left">Rank</th>
                        <th className="game-over-th-left">Player</th>
                        <th className="game-over-th-center">Status</th>
                        <th className="game-over-th-center">Lives</th>
                        <th className="game-over-th-center">Points</th>
                        <th className="game-over-th-center">Answers</th>
                    </tr>
                </thead>
                <tbody>
                    {sortedLeaderboard.map((player, idx) => (
                        <tr key={player.id} className="game-over-tr">
                            <td className="game-over-td-rank">#{idx + 1}</td>
                            <td className="game-over-td-name">{player.display_name}</td>
                            <td className="game-over-td-center">
                                {player.is_alive ? '❤️ Alive' : '💀 Dead'}
                            </td>
                            <td className="game-over-td-center">{player.lives}</td>
                            <td className="game-over-td-points">
                                {player.points}
                            </td>
                            <td className="game-over-td-center">
                                {player.answered_count}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            <div className="game-over-actions">
                <button 
                    onClick={onReturnToHome}
                    className="btn-game-over-home"
                >
                    Return to Home
                </button>
            </div>
        </div>
    );
}

