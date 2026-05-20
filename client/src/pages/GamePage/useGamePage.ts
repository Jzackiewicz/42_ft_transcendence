import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

export function useGamePage() {
    // Retrieve data passed from another page (e.g. from HomePage)
    const location = useLocation();
    const initialUuid = location.state?.sessionUuid || '';

    const [sessionUuid, setSessionUuid] = useState<string>(initialUuid);
    const [messages, setMessages] = useState<string[]>([]);
    const [isConnected, setIsConnected] = useState<boolean>(false);
    
    const wsRef = useRef<WebSocket | null>(null);

    const connectToLobby = () => {
        if (!sessionUuid) return;

        // Connect through Vite proxy
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/game/${sessionUuid}/`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            setIsConnected(true);
            setMessages(prev => [...prev, `[System]: Connected to session ${sessionUuid}`]);
        };

        ws.onmessage = (event) => {
            setMessages(prev => [...prev, `[Server]: ${event.data}`]);
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

    const disconnect = () => {
        if (wsRef.current) {
            wsRef.current.close();
        }
    };

    useEffect(() => {
        if (initialUuid) {
            connectToLobby(); // calling a constructor
        }
        return () => disconnect(); // calling a destructor
    }, []); // Happens only once

    return {
        sessionUuid, setSessionUuid,
        messages, isConnected,
        connectToLobby, disconnect
    };
}