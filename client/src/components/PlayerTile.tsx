import React from 'react';

interface Player {
    id: number;
    display_name: string;
    seat_number: number;
    lives: number;
    points: number;
    answered_count: number;
    is_alive: boolean;
}

interface PlayerTileProps {
    player: Player;
    isCurrentPlayer: boolean;
}

export function PlayerTile({ player, isCurrentPlayer }: PlayerTileProps) {
    const { display_name, seat_number, lives, points, is_alive } = player;

    const tileStyle: React.CSSProperties = {
        padding: '12px 16px',
        border: isCurrentPlayer ? '1px solid var(--cyan)' : '1px solid var(--border)',
        backgroundColor: isCurrentPlayer ? 'var(--tr-cyan)' : 'var(--bg3)',
        borderRadius: 'var(--radius-sm)',
        boxShadow: isCurrentPlayer ? '0 0 15px rgba(0, 229, 255, 0.2)' : 'none',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        fontSize: '13px',
        fontFamily: 'var(--fb)',
        color: is_alive ? 'var(--text)' : 'var(--dim)',
        opacity: is_alive ? 1 : 0.55,
        minWidth: '150px',
        transition: 'all 0.3s ease',
    };

    const nameStyle: React.CSSProperties = {
        fontFamily: 'var(--fd)',
        fontWeight: 700,
        fontSize: '18px',
        color: isCurrentPlayer ? 'var(--cyan)' : 'var(--text)',
        letterSpacing: '0.5px',
    };

    return (
        <div style={tileStyle}>
            <div style={nameStyle}>
                {display_name} {isCurrentPlayer && ' ⚡'}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--dim)', letterSpacing: '0.5px' }}>
                SEAT: {seat_number}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px', fontSize: '13px', fontWeight: 'bold' }}>
                <span>❤️ {lives}</span>
                <span>🏆 {points}</span>
            </div>
            <div style={{ 
                fontSize: '10px', 
                color: is_alive ? 'var(--green)' : 'var(--red)', 
                fontWeight: 700,
                textTransform: 'uppercase',
                marginTop: '4px',
                letterSpacing: '1px'
            }}>
                {is_alive ? '● ALIVE' : '○ ELIMINATED'}
            </div>
        </div>
    );
}
