import React from 'react';

interface LobbyViewProps {
    isHost: boolean;
    playersCount: number;
    onStartGame: () => void;
}

export function LobbyView({ isHost, playersCount, onStartGame }: LobbyViewProps) {
    return (
        <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '4px', backgroundColor: '#f9f9f9' }}>
            <h2>Lobby</h2>
            
            {isHost ? (
                <div>
                    {playersCount < 2 ? (
                        <div style={{ marginBottom: '15px', color: '#666' }}>
                            Waiting for more players to join... (Minimum 2 players required, currently {playersCount})
                        </div>
                    ) : (
                        <div style={{ marginBottom: '15px', color: 'green', fontWeight: 'bold' }}>
                            Ready to start! {playersCount} players in lobby.
                        </div>
                    )}
                    
                    <button 
                        onClick={onStartGame} 
                        disabled={playersCount < 2}
                        style={{ 
                            padding: '10px 20px', 
                            fontSize: '16px', 
                            cursor: playersCount < 2 ? 'not-allowed' : 'pointer' 
                        }}
                    >
                        Start Game
                    </button>
                </div>
            ) : (
                <div style={{ color: '#666', fontStyle: 'italic' }}>
                    Waiting for lobby host to start the game...
                </div>
            )}
        </div>
    );
}
