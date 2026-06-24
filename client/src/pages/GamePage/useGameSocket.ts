import { useState, useEffect, useRef } from 'react';
import { GameSnapshot } from '../../types/Game';
import { connectGameSocket } from '../../api/gameWrapper';

// Messages the client sends to the server over the WebSocket.
export type ClientMessage =
    | { action: 'start_game' }
    | { action: 'leave_game' }
    | { action: 'submit_answer'; payload: { answer: string } }
    | { action: 'nominate_player'; payload: { target_player_id: number } };

const RECONNECT_SCHEDULE_MS = [1000, 2000, 4000, 8000, 16000, 30000];

// Owns the game WebSocket: connection, reconnection, message parsing, and the
// server-time offset used for deadline syncing.
export function useGameSocket(sessionUuid: string) {
    const [gameState, setGameState] = useState<GameSnapshot | null>(null);
    const [myPlayerId, setMyPlayerId] = useState<number | null>(null);
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    const serverTimeOffsetRef = useRef<number>(0);
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
            wsRef.current.onerror = null;
            wsRef.current.close();
        }

        clearReconnectTimer();
        manuallyClosedRef.current = false;

        // Connect through Vite proxy
        const ws = connectGameSocket(sessionUuid);

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

    const disconnect = () => {
        manuallyClosedRef.current = true;
        clearReconnectTimer();
        if (wsRef.current) {
            wsRef.current.onclose = null;
            wsRef.current.onerror = null;
            wsRef.current.close();
            wsRef.current = null;
        }
    };

    /** Current server-aligned timestamp (local clock + observed offset). */
    const getServerNow = () => Date.now() + serverTimeOffsetRef.current;

    /**
     * Notify the server we're leaving, wait briefly for the message to flush,
     * then close the socket and invoke `onDone` (navigation, cleanup, etc.).
     */
    const leaveAndClose = (onDone: () => void) => {
        const finish = () => {
            disconnect();
            onDone();
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

    useEffect(() => {
        if (sessionUuid) {
            connectToLobby();
        }
        return () => disconnect();
    }, []);

    return {
        gameState,
        myPlayerId,
        errorMsg,
        setErrorMsg,
        sendAction,
        getServerNow,
        leaveAndClose,
    };
}
