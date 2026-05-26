import React from 'react';
import { Player } from '../../useGamePage';

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
        <div style={{ padding: '20px', border: '2px solid #f44336', borderRadius: '4px', backgroundColor: '#ffebee' }}>
            <h2 style={{ color: '#d32f2f' }}>Game Over!</h2>

            <div style={{ 
                margin: '20px 0', 
                padding: '15px', 
                backgroundColor: '#fff', 
                borderLeft: '5px solid #f44336',
                borderRadius: '4px' 
            }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>
                    🏆 Winner: {winnerName || 'No winner (Draw)'}
                </div>
                <div style={{ fontSize: '14px', color: '#555' }}>
                    <strong>Reason:</strong> {endReason || 'Game completed.'}
                </div>
            </div>

            <h3>Final Standings</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px', backgroundColor: '#fff' }}>
                <thead>
                    <tr style={{ backgroundColor: '#f2f2f2', borderBottom: '2px solid #ccc' }}>
                        <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Rank</th>
                        <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Player</th>
                        <th style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>Status</th>
                        <th style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>Lives</th>
                        <th style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>Points</th>
                        <th style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>Answers</th>
                    </tr>
                </thead>
                <tbody>
                    {sortedLeaderboard.map((player, idx) => (
                        <tr key={player.id} style={{ borderBottom: '1px solid #ddd' }}>
                            <td style={{ padding: '10px', fontWeight: 'bold', border: '1px solid #ddd' }}>#{idx + 1}</td>
                            <td style={{ padding: '10px', border: '1px solid #ddd' }}>{player.display_name}</td>
                            <td style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>
                                {player.is_alive ? '❤️ Alive' : '💀 Dead'}
                            </td>
                            <td style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>{player.lives}</td>
                            <td style={{ padding: '10px', textAlign: 'center', fontWeight: 'bold', border: '1px solid #ddd' }}>
                                {player.points}
                            </td>
                            <td style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>
                                {player.answered_count}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            <div style={{ marginTop: '20px' }}>
                <button 
                    onClick={onReturnToHome}
                    style={{ 
                        padding: '10px 20px', 
                        fontSize: '16px', 
                        cursor: 'pointer',
                        backgroundColor: '#d32f2f',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '4px',
                        fontWeight: 'bold'
                    }}
                >
                    Return to Home
                </button>
            </div>
        </div>
    );
}
