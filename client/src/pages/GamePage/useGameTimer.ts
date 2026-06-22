import { useState, useEffect } from 'react';
import { GameStatus, GameSnapshot } from '../../types/Game';

// Seconds left until the active phase's server deadline, or null when untimed.
export function useGameTimer(
    gameState: GameSnapshot | null,
    getServerNow: () => number
): number | null {
    const [timeLeft, setTimeLeft] = useState<number | null>(null);

    useEffect(() => {
        if (!gameState) {
            setTimeLeft(null);
            return;
        }

        let deadlineStr: string | null | undefined = null;
        if (gameState.current_status === GameStatus.ANSWERING) {
            deadlineStr = gameState.turn_deadline_at;
        } else if (gameState.current_status === GameStatus.NOMINATION) {
            deadlineStr = gameState.nomination_deadline_at;
        } else if (gameState.current_status === GameStatus.EVALUATION) {
            deadlineStr = gameState.evaluation_deadline_at;
        }

        if (!deadlineStr) {
            setTimeLeft(null);
            return;
        }

        const deadline = new Date(deadlineStr).getTime();

        const updateTimer = () => {
            const diff = deadline - getServerNow();
            setTimeLeft(Math.max(0, Math.ceil(diff / 1000)));
        };

        updateTimer();
        const intervalId = setInterval(updateTimer, 200);

        return () => clearInterval(intervalId);
    }, [gameState?.current_status, gameState?.turn_deadline_at, gameState?.nomination_deadline_at, gameState?.evaluation_deadline_at]);

    return timeLeft;
}
