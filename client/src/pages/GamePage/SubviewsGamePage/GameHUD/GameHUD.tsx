import './GameHUD.css';

interface GameHUDProps {
    questionAskedCount: number;
    totalQuestionsCount: number;
    timeLeft: number | null;
}

export function GameHUD({ questionAskedCount, totalQuestionsCount, timeLeft }: GameHUDProps) {
    return (
        <div className="game-hud-container">
            <div className="hud-progress">
                <span className="hud-label">QUESTION:</span>
                <strong className="hud-value">{questionAskedCount} <span className="hud-muted">of</span> {totalQuestionsCount}</strong>
            </div>

            {timeLeft !== null && (
                <div className={`hud-timer ${timeLeft <= 5 ? 'warning' : ''}`}>
                    <span className="hud-label">TIME LEFT:</span>
                    <strong className="hud-value">🕒 {timeLeft}s</strong>
                </div>
            )}
        </div>
    );
}
