import { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';

export interface Player {
    id: number;
    display_name: string;
    seat_number: number;
    lives: number;
    points: number;
    answered_count: number;
    is_alive: boolean;
    is_online: boolean;
    total_answer_time_ms?: number;
    user_id?: number | null;
    avatar?: string | null;
}

export interface Question {
    id: number;
    question: {
        question_text: string;
        category: string;
    };
    order_index: number;
}

export enum GameStatus {
    LOBBY = 'lobby',
    ANSWERING = 'answering',
    EVALUATION = 'evaluation',
    NOMINATION = 'nomination',
    GAME_OVER = 'game_over'
}

export interface AnswerAttempt {
    id: number;
    answer_text: string | null;
    is_timeout: boolean;
    is_correct: boolean | null;
    evaluation_status: string;
    correct_answer?: string;
    player: number; // player ID
}

export interface GameSnapshot {
    session_uuid: string;
    current_status: GameStatus;
    current_player: number | null;
    host_player: number | null;
    last_correct_player: number | null;
    last_nominated_player: number | null;
    players: Player[];
    is_spectator?: boolean;
    current_question: Question | null;
    current_attempt: AnswerAttempt | null;
    answer_time_limit_ms: number;
    nomination_time_limit_ms: number;
    max_players: number;
    winner: number | null;
    end_reason: string | null;
    question_asked_count: number;
    total_questions_count: number;
    current_attempt_started_at?: string | null;
    turn_deadline_at?: string | null;
    nomination_deadline_at?: string | null;
    evaluation_deadline_at?: string | null;
    server_time?: string | null;
}

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
    const [messages, setMessages] = useState<string[]>([]);
    const [isConnected, setIsConnected] = useState<boolean>(false);
    const [gameState, setGameState] = useState<GameSnapshot | null>(null);
    const [myPlayerId, setMyPlayerId] = useState<number | null>(null);
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    const [timeLeft, setTimeLeft] = useState<number | null>(null);
    const serverTimeOffsetRef = useRef<number>(0);

    // activeGameState directly uses gameState as player_type is removed
    const activeGameState: GameSnapshot | null = gameState;



    const eligiblePlayers = activeGameState?.players.filter(p => p.is_alive) || [];

    // Helper computations
    const currentPlayerObj = myPlayerId !== null
        ? activeGameState?.players.find(p => p.id === myPlayerId)
        : activeGameState?.players.find(p => p.user_id !== null && p.user_id && p.user_id === user?.id);
    const sortedPlayers = [...(activeGameState?.players || [])].sort((a, b) => a.id - b.id);
    const isHost = activeGameState !== null &&
        ((myPlayerId !== null && activeGameState.host_player === myPlayerId) ||
         (myPlayerId === null && sortedPlayers.length > 0 && currentPlayerObj !== undefined && sortedPlayers[0].id === currentPlayerObj.id));
    const hostPlayerId = activeGameState?.host_player ?? (sortedPlayers.length > 0 ? sortedPlayers[0].id : null);
    const gameStarted = activeGameState !== null && activeGameState.current_status !== GameStatus.LOBBY;
    const isGameOver = activeGameState !== null && activeGameState.current_status === GameStatus.GAME_OVER;



    // Timer effect synchronizing with server deadline
    useEffect(() => {
        if (!activeGameState) {
            setTimeLeft(null);
            return;
        }

        let deadlineStr: string | null | undefined = null;

        if (activeGameState.current_status === GameStatus.ANSWERING) {
            deadlineStr = activeGameState.turn_deadline_at;
        } else if (activeGameState.current_status === GameStatus.NOMINATION) {
            deadlineStr = activeGameState.nomination_deadline_at;
        } else if (activeGameState.current_status === GameStatus.EVALUATION) {
            deadlineStr = activeGameState.evaluation_deadline_at;
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
    }, [activeGameState?.current_status, activeGameState?.turn_deadline_at, activeGameState?.nomination_deadline_at, activeGameState?.evaluation_deadline_at]);

    const wsRef = useRef<WebSocket | null>(null);

    const connectToLobby = () => {
        if (!sessionUuid) return;

        if (wsRef.current) {
            wsRef.current.close();
        }

        // Connect through Vite proxy
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/game/${sessionUuid}/`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            setIsConnected(true);
            setMessages(prev => [...prev, `[System]: Connected to session ${sessionUuid}`]);
            setErrorMsg(null);
        };

        ws.onmessage = (event) => {
            setMessages(prev => [...prev, `[Server]: ${event.data}`]);
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

        ws.onclose = () => {
            setIsConnected(false);
            setMessages(prev => [...prev, `[System]: Disconnected`]);
        };

        ws.onerror = (error) => {
            setMessages(prev => [...prev, `[Error]: Check the browser console (F12)`]);
            console.error("WebSocket Error:", error);
        };

        wsRef.current = ws;
    };

    const sendAction = (action: string, payload: any = {}) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            const message = JSON.stringify({ action, payload });
            wsRef.current.send(message);
            setMessages(prev => [...prev, `[Client Send]: ${message}`]);
        } else {
            console.error("WebSocket is not connected");
            setMessages(prev => [...prev, `[System Error]: Cannot send action, WS disconnected`]);
        }
    };

    const startGame = () => {
        sendAction('start_game');
    };

    const submitAnswer = (answer: string) => {
        sendAction('submit_answer', { answer });
    };

    const nominatePlayer = (targetPlayerId: number) => {
        sendAction('nominate_player', { target_player_id: targetPlayerId });
    };

    const disconnect = () => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
    };

    useEffect(() => {
        if (initialUuid) {
            connectToLobby(); // calling a constructor
        }
        return () => disconnect(); // calling a destructor
    }, []); // Happens only once

    const requestAiQuestions = () => {
        // No-op for now (backend integration in separate issue #82)
    };
    const [isAiQuestionsRequested, setIsAiQuestionsRequested] = useState(false);

    const handleRequestAiQuestions = () => {
        requestAiQuestions();
        setIsAiQuestionsRequested(true);
    };
    const leaveGame = () => {
        sendAction('leave_game');
        disconnect();
        setSessionUuid('');
        setActiveSessionUuid(null);
        navigate('/home');
    };

    const connection = {
        sessionUuid,
        setSessionUuid,
        messages,
        isConnected,
        errorMsg,
        setErrorMsg,
        connect: connectToLobby,
        disconnect,
        leaveGame
    };

    const gameActions = {
        startGame,
        submitAnswer,
        nominatePlayer
    };

    const sessionState = {
        gameState: activeGameState,
        eligiblePlayers,
        timeLeft,
        currentPlayerObj,
        isSpectator: activeGameState?.is_spectator ?? false,
        isHost,
        hostPlayerId,
        gameStarted,
        isGameOver,
        sortedPlayers
    };
    return {
        connection,
        gameActions,
        sessionState,
        isAiQuestionsRequested,
        onRequestAiQuestions: handleRequestAiQuestions
    };
}