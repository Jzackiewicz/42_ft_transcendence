import React from 'react';
import { Player } from '../../useGamePage';
import './PlayerTile.css';

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

    const tileClasses = [
        'player-tile',
        isPlayerActive ? 'active' : '',
        !is_alive ? 'eliminated' : ''
    ].filter(Boolean).join(' ');

    return (
        <div className={tileClasses}>
            <div className="player-tile-header">
                <span className={is_alive ? 'player-name-alive' : 'player-name-dead'}>
                    {player.player_type === 'bot' ? '🤖' : '👤'} {display_name} {isCurrentUser && '(You)'}
                </span>
                <span className="player-role-badges">
                    {isPlayerHost && <span title="Lobby Host">👑</span>}
                    {isPlayerActive && <span title="Answering Turn" className="player-role-active">⚡</span>}
                    {isPlayerNominator && <span title="Has Nomination Rights" className="player-role-nominator">🎯</span>}
                </span>
            </div>
            <div className="player-stats-row">
                <div>Lives: {hearts}</div>
                <div>Points: <strong>{points}</strong></div>
            </div>
            {!is_alive && (
                <div className="player-eliminated-label">
                    💀 ELIMINATED
                </div>
            )}
        </div>
    );
}

