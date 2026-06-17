import React from 'react';
import './GameHUD.css';

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
        <div className="game-hud-container">
            {isLobby ? (
                <div className="hud-group">
                    <div className="hud-item">
                        <span className="hud-label">QUESTIONS</span>
                        <strong className="hud-value">{totalQuestionsCount}</strong>
                    </div>
                    {timeLimitSeconds !== undefined && (
                        <div className="hud-item">
                            <span className="hud-label">ANSWER LIMIT</span>
                            <strong className="hud-value">{timeLimitSeconds}s</strong>
                        </div>
                    )}
                    {nominationTimeLimitSeconds !== undefined && (
                        <div className="hud-item">
                            <span className="hud-label">NOMINATION LIMIT</span>
                            <strong className="hud-value">{nominationTimeLimitSeconds}s</strong>
                        </div>
                    )}
                    {maxPlayers !== undefined && (
                        <div className="hud-item">
                            <span className="hud-label">MAX PLAYERS</span>
                            <strong className="hud-value">{maxPlayers}</strong>
                        </div>
                    )}
                </div>
            ) : (
                <div className="hud-group hud-active-game">
                    <div className="hud-item">
                        <span className="hud-label">QUESTION</span>
                        <strong className="hud-value">
                            {questionAskedCount} <span className="hud-muted">of</span> {totalQuestionsCount}
                        </strong>
                    </div>

                    {timeLeft !== null && (
                        <div className={`hud-item hud-timer ${timeLeft <= 5 ? 'warning' : ''}`}>
                            <span className="hud-label">{isEvaluation ? 'TIME TO NEXT STAGE' : 'TIME LEFT'}</span>
                            <strong className="hud-value">{timeLeft}s</strong>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
export default GameHUD;
