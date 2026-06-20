import React from 'react';
import { Button } from '../../../../components/Button/Button';
import { LobbyChat } from '../LobbyChat/LobbyChat';
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
                    
                    <div className="lobby-actions-row">
                        <Button 
                            onClick={onStartGame} 
                            disabled={playersCount < 2}
                        >
                            Start Game
                        </Button>

                        <div className="ai-questions-wrapper">
                            <Button
                                onClick={onRequestAiQuestions}
                                disabled={isAiQuestionsRequested}
                                variant="secondary"
                            >
                                {isAiQuestionsRequested ? '✨ Generation Requested!' : 'Generate AI Questions'}
                            </Button>
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
            <LobbyChat />
        </div>
    );
}
