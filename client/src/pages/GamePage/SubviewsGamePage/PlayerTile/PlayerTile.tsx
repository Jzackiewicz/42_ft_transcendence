import React from 'react';
import { Player } from '../../useGamePage';

interface PlayerTileProps {
    player: Player;
    isCurrentUser: boolean;
    isPlayerHost: boolean;
    isPlayerActive: boolean;
    isPlayerNominator: boolean;
}

export function PlayerTile({
    player,
    isCurrentUser,
    isPlayerHost,
    isPlayerActive,
    isPlayerNominator
}: PlayerTileProps) {
    const { display_name, lives, points, is_alive } = player;

    // Render lives as visual hearts
    const hearts = Array.from({ length: 3 })
        .map((_, i) => i < lives ? '❤️' : '🖤')
        .join('');

    return (
        <div 
            style={{ 
                padding: '10px', 
                border: isPlayerActive ? '2px solid #009688' : '1px solid #ddd', 
                borderRadius: '4px',
                backgroundColor: isPlayerActive ? '#e6fffa' : '#fff',
                opacity: is_alive ? 1 : 0.6
            }}
        >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontWeight: 'bold' }}>
                <span style={{ textDecoration: is_alive ? 'none' : 'line-through' }}>
                    👤 {display_name} {isCurrentUser && '(You)'}
                </span>
                <span style={{ fontSize: '12px' }}>
                    {isPlayerHost && <span title="Lobby Host">👑</span>}
                    {isPlayerActive && <span title="Answering Turn" style={{ marginLeft: '4px', color: '#009688' }}>⚡</span>}
                    {isPlayerNominator && <span title="Has Nomination Rights" style={{ marginLeft: '4px', color: '#3f51b5' }}>🎯</span>}
                </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '5px', fontSize: '13px', color: '#555' }}>
                <div>Lives: {hearts}</div>
                <div>Points: <strong>{points}</strong></div>
            </div>
            {!is_alive && (
                <div style={{ marginTop: '5px', fontSize: '11px', color: '#c62828', fontWeight: 'bold' }}>
                    💀 ELIMINATED
                </div>
            )}
        </div>
    );
}
