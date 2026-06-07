import React from 'react';
import { LobbySettings } from './LobbySettings';
import './LobbyView.css';

interface LobbySettingsObj {
    questionCount: number;
    answerTimeLimitMs: number;
    hasBotPlayer: boolean;
    canAddBot: boolean;
    aiQuestionsRequested: boolean;
    onUpdateSettings: (questions: number, timeLimitSec: number) => void;
    onAddBot: () => void;
    onRemoveBot: () => void;
    onRequestAiQuestions: () => void;
}

interface LobbyViewProps {
    isHost: boolean;
    playersCount: number;
    onStartGame: () => void;
    lobbySettings: LobbySettingsObj;
}

export function LobbyView({
    isHost,
    playersCount,
    onStartGame,
    lobbySettings
}: LobbyViewProps) {
    return (
        <div className="lobby-view-container">
            <h2>Lobby</h2>
            
            {isHost ? (
                <div>
                    {playersCount < 2 ? (
                        <div className="lobby-waiting-more">
                            Waiting for more players to join... (Minimum 2 players required, currently {playersCount})
                        </div>
                    ) : (
                        <div className="lobby-ready">
                            Ready to start! {playersCount} players in lobby.
                        </div>
                    )}
                    
                    <button 
                        onClick={onStartGame} 
                        disabled={playersCount < 2}
                        className="btn-start-game"
                    >
                        Start Game
                    </button>
                </div>
            ) : (
                <div className="lobby-spectator-waiting">
                    Waiting for lobby host to start the game...
                </div>
            )}

            <LobbySettings
                isHost={isHost}
                {...lobbySettings}
            />
        </div>
    );
}

