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
        isCurrentUser ? 'current-user' : '',
        !is_alive ? 'eliminated' : '',
        !player.is_online ? 'offline' : ''
    ].filter(Boolean).join(' ');

    return (
        <div className={tileClasses}>
            <div className="player-tile-header">
                <div className="player-tile-user-info">
                    {player.avatar ? (
                        <img 
                            src={player.avatar} 
                            alt={`${display_name}'s avatar`} 
                            className="player-tile-avatar"
                        />
                    ) : (
                        <span className="player-tile-avatar-placeholder">👤</span>
                    )}
                    <span className={is_alive ? 'player-name-alive' : 'player-name-dead'}>
                        {display_name} {isCurrentUser && '(You)'}
                    </span>
                </div>
                <span className="player-role-badges">
                    {isPlayerHost && <span className="badge badge-host" title="Lobby Host">Host</span>}
                    {isPlayerActive && <span className="badge badge-answering" title="Answering Turn">Answering</span>}
                    {isPlayerNominator && <span className="badge badge-nominator" title="Has Nomination Rights">Nominator</span>}
                </span>
            </div>
            <div className="player-stats">
                <div className="player-stat-item">
                    <span className="stat-label">Lives</span>
                    <span className="stat-hearts">{hearts}</span>
                </div>
                <div className="player-stat-item">
                    <span className="stat-label">Points</span>
                    <span className="stat-points">{points}</span>
                </div>
            </div>
            {!is_alive && (
                <div className="player-eliminated-label">
                    💀 ELIMINATED
                </div>
            )}
            {player.is_online === false && is_alive && (
                <div className="player-offline-label">
                    📡 DISCONNECTED
                </div>
            )}
        </div>
    );
}

