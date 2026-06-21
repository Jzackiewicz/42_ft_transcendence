import { cx } from '../../../../utils/cx';
import styles from './GameHUD.module.css';

interface GameHUDProps {
    questionAskedCount: number;
    totalQuestionsCount: number;
    generatedQuestionsCount?: number;
    timeLeft: number | null;
    timeLimitSeconds?: number;
    nominationTimeLimitSeconds?: number;
    maxPlayers?: number;
    isLobby?: boolean;
    isEvaluation?: boolean;
    isNomination?: boolean;
}

export function GameHUD({
    questionAskedCount,
    totalQuestionsCount,
    generatedQuestionsCount = 0,
    timeLeft,
    timeLimitSeconds,
    nominationTimeLimitSeconds,
    maxPlayers,
    isLobby = false,
    isEvaluation = false,
    isNomination = false
}: GameHUDProps) {
    const timerLabel = isEvaluation
        ? 'TIME TO NEXT STAGE'
        : isNomination
            ? 'RANDOM PICK IN'
            : 'TIMEOUT IN';
    return (
        <div className={styles.gameHudContainer}>
            {isLobby ? (
                <div className={styles.hudGroup}>
                    <div className={styles.hudItem}>
                        <span className={styles.hudLabel}>QUESTIONS</span>
                        <strong className={styles.hudValue}>
                            {totalQuestionsCount - generatedQuestionsCount}
                            {generatedQuestionsCount > 0 && (
                                <span className={styles.hudGenerated}>+ {generatedQuestionsCount} generated</span>
                            )}
                        </strong>
                    </div>
                    {timeLimitSeconds !== undefined && (
                        <div className={styles.hudItem}>
                            <span className={styles.hudLabel}>ANSWER LIMIT</span>
                            <strong className={styles.hudValue}>{timeLimitSeconds}s</strong>
                        </div>
                    )}
                    {nominationTimeLimitSeconds !== undefined && (
                        <div className={styles.hudItem}>
                            <span className={styles.hudLabel}>NOMINATION LIMIT</span>
                            <strong className={styles.hudValue}>{nominationTimeLimitSeconds}s</strong>
                        </div>
                    )}
                    {maxPlayers !== undefined && (
                        <div className={styles.hudItem}>
                            <span className={styles.hudLabel}>MAX PLAYERS</span>
                            <strong className={styles.hudValue}>{maxPlayers}</strong>
                        </div>
                    )}
                </div>
            ) : (
                <div className={cx(styles.hudGroup, styles.hudActiveGame)}>
                    <div className={styles.hudItem}>
                        <span className={styles.hudLabel}>QUESTION</span>
                        <strong className={styles.hudValue}>
                            {questionAskedCount} <span className={styles.hudMuted}>of</span> {totalQuestionsCount}
                        </strong>
                    </div>

                    {timeLeft !== null && (
                        <div className={cx(styles.hudItem, styles.hudTimer, (timeLeft <= 5 && !isEvaluation) && styles.warning)}>
                            <span className={styles.hudLabel}>{timerLabel}</span>
                            <strong className={styles.hudValue}>{timeLeft}s</strong>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
export default GameHUD;
