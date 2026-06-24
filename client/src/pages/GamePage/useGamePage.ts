import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { useGameSocket } from './useGameSocket';
import { useGameTimer } from './useGameTimer';
import { useAiQuestions } from './useAiQuestions';
import { getPlayerContext } from './getPlayerContext';

export function useGamePage() {
    const { user, activeSessionUuid, setActiveSessionUuid } = useUser();

    // Retrieve data passed from another page (e.g. from HomePage)
    const location = useLocation();
    const navigate = useNavigate();

    const initialUuid = location.state?.sessionUuid || activeSessionUuid || '';
    const [sessionUuid, setSessionUuid] = useState<string>(initialUuid);

    useEffect(() => {
        if (sessionUuid) {
            setActiveSessionUuid(sessionUuid);
        }
    }, [sessionUuid, setActiveSessionUuid]);

    const {
        gameState,
        myPlayerId,
        errorMsg,
        setErrorMsg,
        sendAction,
        getServerNow,
        leaveAndClose,
    } = useGameSocket(sessionUuid);

    const { eligiblePlayers, currentPlayerObj, isHost, hostPlayerId } =
        getPlayerContext(gameState, myPlayerId, user?.id);

    const timeLeft = useGameTimer(gameState, getServerNow);

    const startGame = () => {
        sendAction({ action: 'start_game' });
    };

    const submitAnswer = (answer: string) => {
        sendAction({ action: 'submit_answer', payload: { answer } });
    };

    const nominatePlayer = (targetPlayerId: number) => {
        sendAction({ action: 'nominate_player', payload: { target_player_id: targetPlayerId } });
    };

    const { isGeneratingAiQuestions, aiQuestionsGenerated, onRequestAiQuestions } =
        useAiQuestions(sessionUuid, gameState, setErrorMsg);

    const leaveGame = () => {
        leaveAndClose(() => {
            setSessionUuid('');
            setActiveSessionUuid(null);
            navigate('/home');
        });
    };

    const connection = {
        sessionUuid,
        errorMsg,
        setErrorMsg,
        leaveGame
    };

    const gameActions = {
        startGame,
        submitAnswer,
        nominatePlayer
    };

    const sessionState = {
        gameState,
        eligiblePlayers,
        timeLeft,
        currentPlayerObj,
        isSpectator: gameState?.is_spectator ?? false,
        isHost,
        hostPlayerId
    };

    return {
        connection,
        gameActions,
        sessionState,
        isGeneratingAiQuestions,
        aiQuestionsGenerated,
        onRequestAiQuestions
    };
}
