import { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { generateExtraQuestions } from '../../api/gameWrapper';
import { GameStatus, GameSnapshot } from '../../types/Game';

// Messages the client sends to the server over the WebSocket.
type ClientMessage =
    | { action: 'start_game' }
    | { action: 'leave_game' }
    | { action: 'submit_answer'; payload: { answer: string } }
    | { action: 'nominate_player'; payload: { target_player_id: number } };

const RECONNECT_SCHEDULE_MS = [1000, 2000, 4000, 8000, 16000, 30000];

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
    const [gameState, setGameState] = useState<GameSnapshot | null>(null);
    const [myPlayerId, setMyPlayerId] = useState<number | null>(null);
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    const [timeLeft, setTimeLeft] = useState<number | null>(null);
    const serverTimeOffsetRef = useRef<number>(0);

    const eligiblePlayers = gameState?.players.filter(p => p.is_alive) || [];

    // Helper computations
    const currentPlayerObj = myPlayerId !== null
        ? gameState?.players.find(p => p.id === myPlayerId)
        : gameState?.players.find(p => p.user_id !== null && p.user_id && p.user_id === user?.id);
    const sortedPlayers = [...(gameState?.players || [])].sort((a, b) => a.id - b.id);
    const isHost = gameState !== null &&
        ((myPlayerId !== null && gameState.host_player === myPlayerId) ||
         (myPlayerId === null && sortedPlayers.length > 0 && currentPlayerObj !== undefined && sortedPlayers[0].id === currentPlayerObj.id));
    const hostPlayerId = gameState?.host_player ?? (sortedPlayers.length > 0 ? sortedPlayers[0].id : null);

    // Timer effect synchronizing with server deadline
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
            const now = Date.now() + serverTimeOffsetRef.current;
            const diff = deadline - now;
            const secondsLeft = Math.max(0, Math.ceil(diff / 1000));
            setTimeLeft(secondsLeft);
        };

        updateTimer();
        const intervalId = setInterval(updateTimer, 200);

        return () => clearInterval(intervalId);
    }, [gameState?.current_status, gameState?.turn_deadline_at, gameState?.nomination_deadline_at, gameState?.evaluation_deadline_at]);

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectAttemptRef = useRef(0);
    const reconnectTimerRef = useRef<number | null>(null);
    const manuallyClosedRef = useRef(false);

    const clearReconnectTimer = () => {
        if (reconnectTimerRef.current !== null) {
            clearTimeout(reconnectTimerRef.current);
            reconnectTimerRef.current = null;
        }
    };

    const connectToLobby = () => {
        if (!sessionUuid) return;

        if (wsRef.current) {
            wsRef.current.onclose = null;
            wsRef.current.close();
        }

        clearReconnectTimer();
        manuallyClosedRef.current = false;

        // Connect through Vite proxy
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/game/${sessionUuid}/`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            reconnectAttemptRef.current = 0;
            setErrorMsg(null);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.your_player_id !== undefined) {
                    setMyPlayerId(data.your_player_id);
                }
                if (data.snapshot) {
                    const snapshot = data.snapshot as GameSnapshot;
                    if (snapshot.server_time) {
                        serverTimeOffsetRef.current =
                            new Date(snapshot.server_time).getTime() - Date.now();
                    }
                    setGameState(snapshot);
                    setErrorMsg(null);
                } else if (data.type === 'error' || data.error) {
                    setErrorMsg(data.message || data.error || 'Unknown error occurred');
                }
            } catch (err) {
                console.warn("Received non-JSON or unparseable message:", event.data);
            }
        };

        ws.onclose = (event) => {
            if (manuallyClosedRef.current || event.code === 1000) {
                return;
            }

            const idx = Math.min(reconnectAttemptRef.current, RECONNECT_SCHEDULE_MS.length - 1);
            const delay = RECONNECT_SCHEDULE_MS[idx];
            reconnectAttemptRef.current += 1;

            reconnectTimerRef.current = window.setTimeout(() => {
                reconnectTimerRef.current = null;
                connectToLobby();
            }, delay);
        };

        ws.onerror = (error) => {
            console.error("WebSocket Error:", error);
        };

        wsRef.current = ws;
    };

    const sendAction = (message: ClientMessage) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
        } else {
            console.error("WebSocket is not connected");
        }
    };

    const startGame = () => {
        sendAction({ action: 'start_game' });
    };

    const submitAnswer = (answer: string) => {
        sendAction({ action: 'submit_answer', payload: { answer } });
    };

    const nominatePlayer = (targetPlayerId: number) => {
        sendAction({ action: 'nominate_player', payload: { target_player_id: targetPlayerId } });
    };

    const disconnect = () => {
        manuallyClosedRef.current = true;
        clearReconnectTimer();
        if (wsRef.current) {
            wsRef.current.onclose = null;
            wsRef.current.close();
            wsRef.current = null;
        }
    };

    useEffect(() => {
        if (initialUuid) {
            connectToLobby();
        }
        return () => disconnect();
    }, []);

    const [isGeneratingAiQuestions, setIsGeneratingAiQuestions] = useState(false);

    const aiQuestionsGenerated = gameState?.extra_questions_generated ?? false;

    const handleRequestAiQuestions = async () => {
        if (!sessionUuid || isGeneratingAiQuestions || aiQuestionsGenerated) {
            return;
        }
        setIsGeneratingAiQuestions(true);
        setErrorMsg(null);
        try {
            await generateExtraQuestions(sessionUuid);
        } catch (err: any) {
            const detail = err?.response?.data?.error;
            setErrorMsg(
                Array.isArray(detail)
                    ? detail.join(' ')
                    : (detail || 'Failed to generate AI questions. Please try again.')
            );
        } finally {
            setIsGeneratingAiQuestions(false);
        }
    };
    const leaveGame = () => {
        const finish = () => {
            disconnect();
            setSessionUuid('');
            setActiveSessionUuid(null);
            navigate('/home');
        };

        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            finish();
            return;
        }

        sendAction({ action: 'leave_game' });

        const startedAt = Date.now();
        const waitForFlush = () => {
            if (ws.bufferedAmount === 0 || Date.now() - startedAt > 1000) {
                finish();
            } else {
                window.setTimeout(waitForFlush, 50);
            }
        };
        waitForFlush();
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
        onRequestAiQuestions: handleRequestAiQuestions
    };
}