import { Player } from '../../useGamePage';
import { Badge } from '../../../../components/Badge/Badge';
import { Avatar } from '../../../../components/Avatar/Avatar';
import { Icon } from '../../../../components/Icon/Icon';
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
    const hearts = Array.from({ length: 3 }).map((_, i) => (
        <Icon
            key={i}
            name={i < lives ? 'heart' : 'heartOutline'}
            size="xs"
            className={i < lives ? styles.heartFull : styles.heartEmpty}
        />
    ));

    const tileClasses = cx(
        styles.playerTile,
        isPlayerActive && styles.active,
        isCurrentUser && styles.currentUser,
        !is_alive && styles.eliminated,
        !player.is_online && styles.offline,
        isClickable && styles.clickable
    );

    return (
        <div className={tileClasses} onClick={isClickable ? onClick : undefined}>
            <div className={styles.playerTileHeader}>
                <div className={styles.playerTileUserInfo}>
                    <Avatar
                        name={display_name}
                        imageUrl={player.avatar}
                        size="xs"
                        bg="neutral"
                        bordered
                    />
                    <span className={is_alive ? styles.playerNameAlive : styles.playerNameDead}>
                        {display_name} {isCurrentUser && '(You)'}
                    </span>
                </div>
                <span className={styles.playerRoleBadges}>
                    {isPlayerHost && <Badge variant="host" title="Lobby Host">Host</Badge>}
                    {isPlayerActive && <Badge variant="answering" title="Answering Turn">Answering</Badge>}
                    {isPlayerNominator && <Badge variant="nominator" title="Has Nomination Rights">Nominator</Badge>}
                </span>
            </div>
            <div className={styles.playerStats}>
                <div className={styles.playerStatItem}>
                    <span className={styles.statLabel}>Lives</span>
                    <span className={styles.statHearts}>{hearts}</span>
                </div>
                <div className={styles.playerStatItem}>
                    <span className={styles.statLabel}>Points</span>
                    <span className={styles.statPoints}>{points}</span>
                </div>
            </div>
            {!is_alive && (
                <div className={styles.playerEliminatedLabel}>
                    <Icon name="skull" size="sm" /> ELIMINATED
                </div>
            )}
            {player.is_online === false && is_alive && (
                <div className={styles.playerOfflineLabel}>
                    <Icon name="signalOff" size="sm" /> DISCONNECTED
                </div>
            )}
        </div>
    );
}

