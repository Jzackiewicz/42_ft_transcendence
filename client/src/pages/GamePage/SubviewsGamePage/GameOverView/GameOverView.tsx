import React from 'react';
import { Player } from '../../useGamePage';
import './GameOverView.css';

interface GameOverViewProps {
    winnerName: string;
    endReason: string;
    players: Player[];
    onReturnToHome: () => void;
}

export function GameOverView({ winnerName, endReason, players, onReturnToHome }: GameOverViewProps) {
    const sortedLeaderboard = [...players].sort((a, b) => {
        if (b.points !== a.points) return b.points - a.points;
        return b.answered_count - a.answered_count;
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

