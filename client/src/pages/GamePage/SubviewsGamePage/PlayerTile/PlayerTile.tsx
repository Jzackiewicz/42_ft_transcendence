import { Player } from '../../useGamePage';
import { Badge } from '../../../../components/Badge/Badge';
import { cx } from '../../../../utils/cx';
import styles from './PlayerTile.module.css';

interface PlayerTileProps {
    player: Player;
    isCurrentUser: boolean;
    isPlayerHost: boolean;
    isPlayerActive: boolean;
    isPlayerNominator: boolean;
    isClickable?: boolean;
    onClick?: () => void;
}

export function PlayerTile({
    player,
    isCurrentUser,
    isPlayerHost,
    isPlayerActive,
    isPlayerNominator,
    isClickable = false,
    onClick
}: PlayerTileProps) {
    const { display_name, lives, points, is_alive } = player;

    // Render lives as visual hearts
    const hearts = Array.from({ length: 3 })
        .map((_, i) => i < lives ? '❤️' : '🖤')
        .join('');

    const tileClasses = cx(
        styles['player-tile'],
        isPlayerActive && styles.active,
        isCurrentUser && styles['current-user'],
        !is_alive && styles.eliminated,
        !player.is_online && styles.offline,
        isClickable && styles.clickable
    );

    return (
        <div className={tileClasses} onClick={isClickable ? onClick : undefined}>
            <div className={styles['player-tile-header']}>
                <div className={styles['player-tile-user-info']}>
                    {player.avatar ? (
                        <img
                            src={player.avatar}
                            alt={`${display_name}'s avatar`}
                            className={styles['player-tile-avatar']}
                        />
                    ) : (
                        <span className={styles['player-tile-avatar-placeholder']}>👤</span>
                    )}
                    <span className={is_alive ? styles['player-name-alive'] : styles['player-name-dead']}>
                        {display_name} {isCurrentUser && '(You)'}
                    </span>
                </div>
                <span className={styles['player-role-badges']}>
                    {isPlayerHost && <Badge variant="host" title="Lobby Host">Host</Badge>}
                    {isPlayerActive && <Badge variant="answering" title="Answering Turn">Answering</Badge>}
                    {isPlayerNominator && <Badge variant="nominator" title="Has Nomination Rights">Nominator</Badge>}
                </span>
            </div>
            <div className={styles['player-stats']}>
                <div className={styles['player-stat-item']}>
                    <span className={styles['stat-label']}>Lives</span>
                    <span className={styles['stat-hearts']}>{hearts}</span>
                </div>
                <div className={styles['player-stat-item']}>
                    <span className={styles['stat-label']}>Points</span>
                    <span className={styles['stat-points']}>{points}</span>
                </div>
            </div>
            {!is_alive && (
                <div className={styles['player-eliminated-label']}>
                    💀 ELIMINATED
                </div>
            )}
            {player.is_online === false && is_alive && (
                <div className={styles['player-offline-label']}>
                    📡 DISCONNECTED
                </div>
            )}
        </div>
    );
}

