import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGamePage } from './useGamePage';
import { PlayerTile } from '../../components/PlayerTile';
import { useUser } from '../../context/UserContext';

export function GamePage() {
    const { user } = useUser();
    const navigate = useNavigate();
    
    // Extract variables and functions from the custom hook
    const { 
        sessionUuid, 
        messages, 
        isConnected, 
        gameState, 
        errorMsg, 
        setErrorMsg,
        startGame, 
        submitAnswer, 
        nominatePlayer, 
        disconnect 
    } = useGamePage();

    const [answerText, setAnswerText] = useState('');
    const [selectedNomineeId, setSelectedNomineeId] = useState<number | ''>('');

    const eligiblePlayers = gameState?.players.filter(p => p.is_alive) || [];

    React.useEffect(() => {
        if (eligiblePlayers.length > 0) {
            if (!selectedNomineeId || !eligiblePlayers.some(p => p.id === selectedNomineeId)) {
                setSelectedNomineeId(eligiblePlayers[0].id);
            }
        } else {
            setSelectedNomineeId('');
        }
    }, [gameState?.players, user?.username, eligiblePlayers.length]);

    const handleLeave = () => {
        disconnect();
        navigate('/home');
    };

    const handleAnswerSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        submitAnswer(answerText);
        setAnswerText(''); // clear input
    };

    // Current player in this session
    const currentPlayerObj = gameState?.players.find(p => p.display_name === user?.username);

    const sortedPlayers = [...(gameState?.players || [])].sort((a, b) => a.id - b.id);
    const isHost = currentPlayerObj && sortedPlayers.length > 0 && currentPlayerObj.id === sortedPlayers[0].id;

    const activePlayerObj = gameState?.players.find(p => p.id === gameState.current_player);
    
    const nominationHolderObj = gameState?.players.find(p => p.id === gameState.last_correct_player);

    const containerStyle: React.CSSProperties = {
        display: 'flex',
        flexDirection: 'row',
        gap: '24px',
        fontFamily: 'var(--fb)',
        padding: '40px 20px',
        maxWidth: '1200px',
        margin: '0 auto',
        color: 'var(--text)',
        flexWrap: 'wrap'
    };

    const mainPanelStyle: React.CSSProperties = {
        flex: 2,
        minWidth: '320px',
        padding: '30px',
        border: '1px solid var(--border)',
        backgroundColor: 'var(--bg2)',
        borderRadius: 'var(--radius-md)',
        boxShadow: '0 8px 30px rgba(0,0,0,0.5)'
    };

    const logsPanelStyle: React.CSSProperties = {
        flex: 1,
        minWidth: '280px',
        padding: '30px',
        border: '1px solid var(--border)',
        backgroundColor: 'var(--bg2)',
        display: 'flex',
        flexDirection: 'column',
        height: '650px',
        borderRadius: 'var(--radius-md)',
        boxShadow: '0 8px 30px rgba(0,0,0,0.5)'
    };

    const buttonStyle: React.CSSProperties = {
        padding: '10px 20px',
        border: 'none',
        borderRadius: 'var(--radius-sm)',
        background: 'linear-gradient(135deg, var(--cyan), var(--magenta))',
        color: 'var(--bg)',
        cursor: 'pointer',
        fontWeight: 'bold',
        fontFamily: 'var(--fd)',
        fontSize: '15px',
        letterSpacing: '1px',
        textTransform: 'uppercase',
        boxShadow: '0 0 15px rgba(0, 229, 255, 0.2)',
        transition: 'all 0.2s ease',
    };

    const secondaryButtonStyle: React.CSSProperties = {
        padding: '10px 20px',
        border: '1px solid var(--cyan)',
        borderRadius: 'var(--radius-sm)',
        backgroundColor: 'var(--tr-cyan)',
        color: 'var(--cyan)',
        cursor: 'pointer',
        fontWeight: 'bold',
        fontFamily: 'var(--fd)',
        fontSize: '14px',
        letterSpacing: '0.5px',
        textTransform: 'uppercase',
        transition: 'all 0.2s ease',
    };

    const disconnectButtonStyle: React.CSSProperties = {
        padding: '8px 16px',
        border: '1px solid var(--red)',
        borderRadius: 'var(--radius-sm)',
        backgroundColor: 'rgba(255, 23, 68, 0.1)',
        color: 'var(--red)',
        cursor: 'pointer',
        fontWeight: 'bold',
        fontFamily: 'var(--fd)',
        fontSize: '13px',
        letterSpacing: '0.5px',
        textTransform: 'uppercase',
        transition: 'all 0.2s ease',
    };

    const inputStyle: React.CSSProperties = {
        padding: '10px 14px',
        border: '1px solid var(--pb)',
        backgroundColor: 'var(--bg3)',
        color: 'var(--text)',
        borderRadius: 'var(--radius-sm)',
        fontFamily: 'var(--fb)',
        fontSize: '15px',
        outline: 'none',
        flex: 1,
        transition: 'border-color 0.2s',
    };

    return (
        <div style={containerStyle}>
            <div style={mainPanelStyle}>
                <h1 style={{ fontFamily: 'var(--fd)', fontSize: '36px', textTransform: 'uppercase', letterSpacing: '1.5px', marginBottom: '25px', background: 'linear-gradient(135deg, var(--cyan), var(--magenta))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Game Session
                </h1>
                
                <div style={{ marginBottom: '25px', padding: '15px 20px', border: '1px solid var(--border)', backgroundColor: 'var(--bg3)', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ fontSize: '14px', color: 'var(--dim)', marginBottom: '4px' }}>SESSION CODE:</div>
                    <div style={{ fontFamily: 'monospace', fontSize: '16px', fontWeight: 'bold', wordBreak: 'break-all', color: 'var(--cyan)' }}>
                        {sessionUuid || 'None'}
                    </div>
                    <div style={{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}>
                        <span style={{ color: isConnected ? 'var(--green)' : 'var(--red)' }}>●</span>
                        <strong>CONNECTION:</strong>{' '}
                        <span style={{ fontWeight: 'bold', color: isConnected ? 'var(--green)' : 'var(--red)', letterSpacing: '0.5px' }}>
                            {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
                        </span>
                    </div>
                </div>

                {errorMsg && (
                    <div style={{ 
                        padding: '12px 18px', 
                        border: '1px solid var(--red)',
                        backgroundColor: 'rgba(255, 23, 68, 0.1)',
                        color: 'var(--red)',
                        marginBottom: '20px',
                        borderRadius: 'var(--radius-sm)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        fontSize: '14px'
                    }}>
                        <span><strong>Error:</strong> {errorMsg}</span>
                        <button onClick={() => setErrorMsg(null)} style={{ border: 'none', background: 'transparent', cursor: 'pointer', fontWeight: 'bold', color: 'var(--red)', fontSize: '16px' }}>×</button>
                    </div>
                )}

                {gameState ? (
                    <div>
                        <div style={{ 
                            padding: '12px 20px', 
                            border: '1px solid var(--border)',
                            backgroundColor: 'var(--bg3)',
                            borderRadius: 'var(--radius-sm)',
                            marginBottom: '25px',
                            fontWeight: 'bold',
                            fontSize: '14px',
                            letterSpacing: '1px',
                            color: 'var(--cyan)'
                        }}>
                            GAME STATUS: {gameState.current_status}
                        </div>

                        <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid var(--border)', backgroundColor: 'var(--bg3)', borderRadius: 'var(--radius-sm)' }}>
                            <h2 style={{ fontFamily: 'var(--fd)', fontSize: '20px', letterSpacing: '0.5px', textTransform: 'uppercase', marginBottom: '15px', color: 'var(--text)' }}>
                                Players
                            </h2>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                                {gameState.players && gameState.players.length > 0 ? (
                                    gameState.players.map((player) => (
                                        <PlayerTile 
                                            key={player.id} 
                                            player={player} 
                                            isCurrentPlayer={player.id === gameState.current_player} 
                                        />
                                    ))
                                ) : (
                                    <p style={{ color: 'var(--dim)' }}>No players in lobby yet.</p>
                                )}
                            </div>
                        </div>

                        {gameState.current_question && (
                            <div style={{ 
                                padding: '20px', 
                                border: '1px dashed var(--cyan)', 
                                backgroundColor: 'var(--bg3)', 
                                borderRadius: 'var(--radius-sm)',
                                marginBottom: '30px' 
                            }}>
                                <span style={{ 
                                    fontSize: '11px', 
                                    border: '1px solid var(--magenta)',
                                    color: 'var(--magenta)',
                                    padding: '3px 8px', 
                                    fontWeight: 'bold',
                                    borderRadius: '4px',
                                    letterSpacing: '1px'
                                }}>
                                    {gameState.current_question.question.category.toUpperCase()}
                                </span>
                                <h3 style={{ margin: '18px 0 12px 0', fontFamily: 'var(--fb)', fontSize: '18px', lineHeight: '1.5' }}>
                                    {gameState.current_question.question.question_text}
                                </h3>
                                <div style={{ fontSize: '12px', color: 'var(--dim)' }}>
                                    Question {gameState.question_asked_count} of {gameState.total_questions_count}
                                </div>
                            </div>
                        )}

                        <form onSubmit={handleAnswerSubmit} style={{ marginBottom: '20px', display: 'flex', flexDirection: 'column', gap: '8px', maxWidth: '500px' }}>
                            <label htmlFor="answer-input" style={{ fontWeight: 'bold', fontSize: '14px', color: 'var(--text)' }}>
                                Your Answer:
                            </label>
                            <input 
                                id="answer-input"
                                type="text" 
                                placeholder="Type your answer here..." 
                                value={answerText} 
                                onChange={(e) => setAnswerText(e.target.value)}
                                style={inputStyle}
                                onFocus={(e) => (e.currentTarget.style.borderColor = 'var(--cyan)')}
                                onBlur={(e) => (e.currentTarget.style.borderColor = 'var(--pb)')}
                            />
                        </form>

                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap', marginBottom: '25px' }}>
                            {/* 1. Start Game */}
                            <button onClick={startGame} style={buttonStyle}>
                                Start Game
                            </button>
                            
                            {/* 2. Submit Answer */}
                            <button onClick={() => { submitAnswer(answerText); setAnswerText(''); }} style={buttonStyle}>
                                Submit Answer
                            </button>

                            {/* 3. Nominate Player (with dropdown) */}
                            <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                                <button 
                                    onClick={() => selectedNomineeId && nominatePlayer(Number(selectedNomineeId))} 
                                    style={buttonStyle}
                                    disabled={!selectedNomineeId}
                                >
                                    Nominate Player
                                </button>
                                <select 
                                    value={selectedNomineeId} 
                                    onChange={(e) => setSelectedNomineeId(e.target.value ? Number(e.target.value) : '')}
                                    style={{
                                        padding: '10px 14px',
                                        border: '1px solid var(--pb)',
                                        borderRadius: 'var(--radius-sm)',
                                        backgroundColor: 'var(--bg3)',
                                        color: 'var(--text)',
                                        fontFamily: 'var(--fb)',
                                        fontSize: '14px',
                                        outline: 'none',
                                        cursor: 'pointer',
                                        height: '40px',
                                        boxSizing: 'border-box'
                                    }}
                                >
                                    <option value="">-- Nominee --</option>
                                    {eligiblePlayers.map(p => (
                                        <option key={p.id} value={p.id}>
                                            {p.display_name} {p.display_name === user?.username ? ' (You)' : ''}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* 4. Leave */}
                            <button onClick={handleLeave} style={disconnectButtonStyle}>
                                Leave
                            </button>
                        </div>
                    </div>
                ) : (
                    <div style={{ textAlign: 'center', padding: '50px 0', border: '1px solid var(--border)', backgroundColor: 'var(--bg3)', borderRadius: 'var(--radius-sm)', color: 'var(--dim)' }}>
                        <h3 style={{ fontFamily: 'var(--fd)', fontSize: '22px', textTransform: 'uppercase', color: 'var(--cyan)', marginBottom: '8px' }}>Waiting for Game Snapshot...</h3>
                        <p style={{ fontSize: '14px' }}>Connection established. Awaiting state from the server...</p>
                    </div>
                )}


            </div>

            <div style={logsPanelStyle}>
                <h2 style={{ fontFamily: 'var(--fd)', fontSize: '20px', letterSpacing: '0.5px', textTransform: 'uppercase', marginBottom: '15px', color: 'var(--text)' }}>
                    WebSocket Live Console
                </h2>
                <div style={{ 
                    flex: 1, 
                    border: '1px solid var(--border)', 
                    padding: '15px', 
                    backgroundColor: 'var(--bg3)', 
                    color: 'var(--text)', 
                    fontFamily: 'monospace', 
                    fontSize: '12px', 
                    overflowY: 'auto',
                    borderRadius: 'var(--radius-sm)',
                    lineHeight: '1.5'
                }}>
                    {messages.length > 0 ? (
                        <ul style={{ listStyleType: 'none', padding: 0, margin: 0 }}>
                            {messages.map((msg, index) => {
                                let itemColor = 'var(--text)';
                                if (msg.includes('[Error]')) itemColor = 'var(--red)';
                                else if (msg.includes('[System]')) itemColor = 'var(--cyan)';
                                else if (msg.includes('[Received]')) itemColor = 'var(--green)';

                                return (
                                    <li key={index} style={{ marginBottom: '8px', wordBreak: 'break-all', color: itemColor }}>
                                        {msg}
                                    </li>
                                );
                            })}
                        </ul>
                    ) : (
                        <span style={{ color: 'var(--placeholder)' }}>No WS traffic recorded yet.</span>
                    )}
                </div>
            </div>
        </div>
    );
}