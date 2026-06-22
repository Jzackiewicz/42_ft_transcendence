import { Player } from '../../useGamePage';
import { Button } from '../../../../components/Button/Button';
import { Avatar } from '../../../../components/Avatar/Avatar';
import { Icon } from '../../../../components/Icon/Icon';
import { cx } from '../../../../utils/cx';
import styles from './GameOverView.module.css';

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
        Array.from({ length: 3 }).map((_, i) => (
            <Icon
                key={i}
                name={i < lives ? 'heart' : 'heartOutline'}
                size="xs"
                className={i < lives ? styles.heartFull : styles.heartEmpty}
            />
        ));

    return (
        <div className={styles.gameOverContainer}>

            <table className={styles.gameOverTable}>
                <thead className={styles.gameOverThead}>
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
                        const rowClasses = cx(
                            styles.gameOverRow,
                            isWinner && styles.winnerRow,
                            !player.is_alive && styles.eliminatedRow
                        );

                        return (
                            <tr key={player.id} className={rowClasses}>
                                <td className={styles.gameOverRank}>
                                    #{idx + 1}
                                </td>
                                <td className={styles.gameOverPlayerCell}>
                                    <div className={styles.gameOverPlayerInfo}>
                                        <Avatar
                                            name={player.display_name}
                                            imageUrl={player.avatar}
                                            size="sm"
                                            bg="neutral"
                                            bordered
                                        />
                                        <span className={styles.gameOverPlayerName}>
                                            {player.display_name}
                                        </span>
                                    </div>
                                </td>
                                <td className={styles.gameOverPoints}>
                                    {player.points}
                                </td>
                                <td className={styles.gameOverLives}>
                                    {renderHearts(player.lives)}
                                </td>
                                <td className={styles.gameOverAnswers}>
                                    {player.answered_count}
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>

            {/* ── Actions ────────────────────────────────────────── */}
            <div className={styles.gameOverActions}>
                <Button onClick={onReturnToHome}>
                    Return to Home
                </Button>
            </div>

        </div>
    );
}
