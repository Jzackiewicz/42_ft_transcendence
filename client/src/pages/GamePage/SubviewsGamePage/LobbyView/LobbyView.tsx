import React from 'react';
import { LobbySettings } from './LobbySettings';
import './LobbyView.css';

interface LobbyViewProps {
    isHost: boolean;
    playersCount: number;
    onStartGame: () => void;
    // Lobby configuration settings
    questionCount: number;
    answerTimeLimitMs: number;
    hasBotPlayer: boolean;
    canAddBot: boolean;
    onUpdateSettings: (questions: number, timeLimitSec: number) => void;
    onAddBot: () => void;
    onRemoveBot: () => void;
    onRequestAiQuestions: () => void;
    aiQuestionsRequested: boolean;
}

export function LobbyView({
    isHost,
    playersCount,
    onStartGame,
    questionCount,
    answerTimeLimitMs,
    hasBotPlayer,
    canAddBot,
    onUpdateSettings,
    onAddBot,
    onRemoveBot,
    onRequestAiQuestions,
    aiQuestionsRequested
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
                questionCount={questionCount}
                answerTimeLimitMs={answerTimeLimitMs}
                hasBotPlayer={hasBotPlayer}
                canAddBot={canAddBot}
                onUpdateSettings={onUpdateSettings}
                onAddBot={onAddBot}
                onRemoveBot={onRemoveBot}
                onRequestAiQuestions={onRequestAiQuestions}
                aiQuestionsRequested={aiQuestionsRequested}
            />
        </div>
    );
}

