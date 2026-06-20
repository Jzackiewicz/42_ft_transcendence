import React from 'react';
import { cx } from '../../../../utils/cx';
import styles from './GameHUD.module.css';

interface GameHUDProps {
    questionAskedCount: number;
    totalQuestionsCount: number;
    timeLeft: number | null;
    timeLimitSeconds?: number;
    nominationTimeLimitSeconds?: number;
    maxPlayers?: number;
    isLobby?: boolean;
    isEvaluation?: boolean;
}

export function GameHUD({ 
    questionAskedCount, 
    totalQuestionsCount, 
    timeLeft, 
    timeLimitSeconds, 
    nominationTimeLimitSeconds,
    maxPlayers,
    isLobby = false,
    isEvaluation = false
}: GameHUDProps) {
    return (
        <div className={styles['game-hud-container']}>
            {isLobby ? (
                <div className={styles['hud-group']}>
                    <div className={styles['hud-item']}>
                        <span className={styles['hud-label']}>QUESTIONS</span>
                        <strong className={styles['hud-value']}>{totalQuestionsCount}</strong>
                    </div>
                    {timeLimitSeconds !== undefined && (
                        <div className={styles['hud-item']}>
                            <span className={styles['hud-label']}>ANSWER LIMIT</span>
                            <strong className={styles['hud-value']}>{timeLimitSeconds}s</strong>
                        </div>
                    )}
                    {nominationTimeLimitSeconds !== undefined && (
                        <div className={styles['hud-item']}>
                            <span className={styles['hud-label']}>NOMINATION LIMIT</span>
                            <strong className={styles['hud-value']}>{nominationTimeLimitSeconds}s</strong>
                        </div>
                    )}
                    {maxPlayers !== undefined && (
                        <div className={styles['hud-item']}>
                            <span className={styles['hud-label']}>MAX PLAYERS</span>
                            <strong className={styles['hud-value']}>{maxPlayers}</strong>
                        </div>
                    )}
                </div>
            ) : (
                <div className={cx(styles['hud-group'], styles['hud-active-game'])}>
                    <div className={styles['hud-item']}>
                        <span className={styles['hud-label']}>QUESTION</span>
                        <strong className={styles['hud-value']}>
                            {questionAskedCount} <span className={styles['hud-muted']}>of</span> {totalQuestionsCount}
                        </strong>
                    </div>

                    {timeLeft !== null && (
                        <div className={cx(styles['hud-item'], styles['hud-timer'], (timeLeft <= 5 && !isEvaluation) && styles.warning)}>
                            <span className={styles['hud-label']}>{isEvaluation ? 'TIME TO NEXT STAGE' : 'TIME LEFT'}</span>
                            <strong className={styles['hud-value']}>{timeLeft}s</strong>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
export default GameHUD;
