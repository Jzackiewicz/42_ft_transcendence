import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { useUser } from '../../context/UserContext';

export interface Player {
    id: number;
    display_name: string;
    seat_number: number;
    lives: number;
    points: number;
    answered_count: number;
    is_alive: boolean;
}

export interface Question {
    id: number;
    question: {
        question_text: string;
        category: string;
    };
    order_index: number;
}

export interface GameSnapshot {
    session_uuid: string;
    current_status: string; // 'LOBBY', 'ANSWERING', 'EVALUATION', 'NOMINATION', 'GAME_OVER'
    current_player: number | null;
    last_correct_player: number | null;
    last_nominated_player: number | null;
    players: Player[];
    current_question: Question | null;
    answer_time_limit_ms: number;
    winner: number | null;
    end_reason: string | null;
    question_asked_count: number;
    total_questions_count: number;
    current_attempt_started_at?: string | null;
    turn_deadline_at?: string | null;
}

export function useGamePage() {
    const { user } = useUser();

    // Retrieve data passed from another page (e.g. from HomePage)
    const location = useLocation();
    const initialUuid = location.state?.sessionUuid || '';

    const [sessionUuid, setSessionUuid] = useState<string>(initialUuid);
    const [messages, setMessages] = useState<string[]>([]);
    const [isConnected, setIsConnected] = useState<boolean>(false);
    const [gameState, setGameState] = useState<GameSnapshot | null>(null);
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    const [answerText, setAnswerText] = useState('');
    const [selectedNomineeId, setSelectedNomineeId] = useState<number | ''>('');
    const [timeLeft, setTimeLeft] = useState<number | null>(null);

    const eligiblePlayers = gameState?.players.filter(p => p.is_alive) || [];

    // Helper computations
    const currentPlayerObj = gameState?.players.find(p => p.display_name === user?.username);
    const sortedPlayers = [...(gameState?.players || [])].sort((a, b) => a.id - b.id);
    const isHost = sortedPlayers.length > 0 && currentPlayerObj !== undefined && (sortedPlayers[0].id === currentPlayerObj.id);
    const hostPlayerId = sortedPlayers.length > 0 ? sortedPlayers[0].id : null;
    const gameStarted = gameState !== null && gameState.current_status.toUpperCase() !== 'LOBBY';
    const isGameOver = gameState !== null && gameState.current_status.toUpperCase() === 'GAME_OVER';

    useEffect(() => {
        if (eligiblePlayers.length > 0) {
            if (!selectedNomineeId || !eligiblePlayers.some(p => p.id === selectedNomineeId)) {
                setSelectedNomineeId(eligiblePlayers[0].id);
            }
        } else {
            setSelectedNomineeId('');
        }
    }, [gameState?.players, user?.username, eligiblePlayers.length]);

    // Timer effect synchronizing with server turn_deadline_at
    useEffect(() => {
        if (!gameState || gameState.current_status.toUpperCase() !== 'ANSWERING' || !gameState.turn_deadline_at) {
            setTimeLeft(null);
            return;
        }

        const deadline = new Date(gameState.turn_deadline_at).getTime();

        const updateTimer = () => {
            const now = new Date().getTime();
            const diff = deadline - now;
            const secondsLeft = Math.max(0, Math.ceil(diff / 1000));
            setTimeLeft(secondsLeft);
        };

        updateTimer();
        const intervalId = setInterval(updateTimer, 200);

        return () => clearInterval(intervalId);
    }, [gameState?.current_status, gameState?.turn_deadline_at]);

    const wsRef = useRef<WebSocket | null>(null);
    const closeTimeoutRef = useRef<any>(null);

    const connectToLobby = () => {
        if (!sessionUuid) return;

        if (closeTimeoutRef.current) {
            clearTimeout(closeTimeoutRef.current);
            closeTimeoutRef.current = null;
            if (wsRef.current && (wsRef.current.readyState === WebSocket.CONNECTING || wsRef.current.readyState === WebSocket.OPEN)) {
                return;
            }
        }

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
                if (data.snapshot) {
                    setGameState(data.snapshot);
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
        if (closeTimeoutRef.current) {
            clearTimeout(closeTimeoutRef.current);
            closeTimeoutRef.current = null;
        }
        if (wsRef.current) {
            closeTimeoutRef.current = setTimeout(() => {
                if (wsRef.current) {
                    wsRef.current.close();
                    wsRef.current = null;
                }
                closeTimeoutRef.current = null;
            }, 100);
        }
    };

    useEffect(() => {
        if (initialUuid) {
            connectToLobby(); // calling a constructor
        }
        return () => disconnect(); // calling a destructor
    }, []); // Happens only once

    return {
        sessionUuid,
        setSessionUuid,
        messages,
        isConnected,
        gameState,
        errorMsg,
        setErrorMsg,
        startGame,
        submitAnswer,
        nominatePlayer,
        connectToLobby,
        disconnect,
        answerText,
        setAnswerText,
        selectedNomineeId,
        setSelectedNomineeId,
        eligiblePlayers,
        timeLeft,
        currentPlayerObj,
        isHost,
        hostPlayerId,
        gameStarted,
        isGameOver,
        sortedPlayers
    };
}