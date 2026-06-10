import React from 'react';
import './LobbyView.css';

interface LobbyViewProps {
    isHost: boolean;
    playersCount: number;
    onStartGame: () => void;
    isAiQuestionsRequested: boolean;
    onRequestAiQuestions: () => void;
}

export function LobbyView({
    isHost,
    playersCount,
    onStartGame,
    isAiQuestionsRequested,
    onRequestAiQuestions
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

                    <div className="lobby-ai-actions">
                        <div className="ai-questions-section">
                            <button
                                onClick={onRequestAiQuestions}
                                className="btn-secondary"
                                disabled={isAiQuestionsRequested}
                            >
                                {isAiQuestionsRequested ? '✨ Generation Requested!' : 'Generate AI Questions'}
                            </button>
                            {isAiQuestionsRequested && (
                                <span className="ai-feedback-toast">
                                    ✓ AI Questions successfully queued!
                                </span>
                            )}
                        </div>
                    </div>
                </div>
            ) : (
                <div className="lobby-spectator-waiting">
                    Waiting for lobby host to start the game...
                </div>
            )}
        </div>
    );
}
