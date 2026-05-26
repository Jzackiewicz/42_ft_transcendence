import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useGamePage } from './useGamePage';
import { useUser } from '../../context/UserContext';
import { LobbyView } from './SubviewsGamePage/LobbyView/LobbyView';
import { AnsweringView } from './SubviewsGamePage/AnsweringView/AnsweringView';
import { NominationView } from './SubviewsGamePage/NominationView/NominationView';
import { EvaluationView } from './SubviewsGamePage/EvaluationView/EvaluationView';
import { GameOverView } from './SubviewsGamePage/GameOverView/GameOverView';
import { PlayerTile } from './SubviewsGamePage/PlayerTile/PlayerTile';

export function GamePage() {
    const { user } = useUser();
    const navigate = useNavigate();

    const {
        sessionUuid,
        gameState,
        errorMsg,
        setErrorMsg,
        startGame,
        submitAnswer,
        nominatePlayer,
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
        isGameOver
    } = useGamePage();

    const handleLeave = () => {
        disconnect();
        navigate('/home');
    };

    const handleAnswerSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        submitAnswer(answerText);
        setAnswerText('');
    };

    const handleNominateSubmit = () => {
        if (selectedNomineeId) {
            nominatePlayer(selectedNomineeId);
        }
    };

    const renderActiveView = () => {
        if (!gameState) return null;

        const statusUpper = gameState.current_status.toUpperCase();

        switch (statusUpper) {
            case 'LOBBY':
                return (
                    <LobbyView 
                        isHost={isHost}
                        playersCount={gameState.players.length}
                        onStartGame={startGame}
                    />
                );
            case 'ANSWERING':
                return (
                    <AnsweringView 
                        questionText={gameState.current_question?.question?.question_text || ''}
                        category={gameState.current_question?.question?.category || ''}
                        isCurrentAnswering={gameState.current_player === currentPlayerObj?.id}
                        activePlayerName={gameState.players.find(p => p.id === gameState.current_player)?.display_name || 'Someone'}
                        answerText={answerText}
                        setAnswerText={setAnswerText}
                        onSubmitAnswer={handleAnswerSubmit}
                        timeLeft={timeLeft}
                    />
                );
            case 'NOMINATION':
                return (
                    <NominationView 
                        isCurrentNominator={gameState.last_correct_player === currentPlayerObj?.id}
                        nominatorName={gameState.players.find(p => p.id === gameState.last_correct_player)?.display_name || 'Someone'}
                        eligiblePlayers={eligiblePlayers}
                        selectedNomineeId={selectedNomineeId}
                        setSelectedNomineeId={setSelectedNomineeId}
                        onNominatePlayer={handleNominateSubmit}
                    />
                );
            case 'EVALUATION':
                return <EvaluationView />;
            case 'GAME_OVER':
                return (
                    <GameOverView 
                        winnerName={gameState.players.find(p => p.id === gameState.winner)?.display_name || ''}
                        endReason={gameState.end_reason || ''}
                        players={gameState.players}
                        onReturnToHome={handleLeave}
                    />
                );
            default:
                return (
                    <div>
                        Unknown game status: {gameState.current_status}
                    </div>
                );
        }
    };



    // If game is over, we replace the entire view as requested
    if (isGameOver) {
        return (
            <div style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '800px', margin: '0 auto' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h1>Quizscendence</h1>
                    <div><strong>Session Code:</strong> {sessionUuid}</div>
                </div>
                {renderActiveView()}
            </div>
        );
    }

    return (
        <div style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '1000px', margin: '0 auto' }}>
            {/* Top Bar (Session Code & Leave Button) */}
            <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                borderBottom: '1px solid #ccc', 
                paddingBottom: '10px',
                marginBottom: '20px'
            }}>
                <h1>Quizscendence</h1>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div><strong>SESSION CODE:</strong> {sessionUuid || 'None'}</div>
                    <button onClick={handleLeave} style={{ padding: '6px 12px', cursor: 'pointer' }}>Leave Game</button>
                </div>
            </div>

            {/* Error Banner */}
            {errorMsg && (
                <div style={{ 
                    color: '#721c24', 
                    backgroundColor: '#f8d7da', 
                    border: '1px solid #f5c6cb', 
                    padding: '10px', 
                    margin: '10px 0',
                    borderRadius: '4px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <span><strong>Error:</strong> {errorMsg}</span>
                    <button 
                        onClick={() => setErrorMsg(null)} 
                        style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', color: '#721c24' }}
                    >
                        &times;
                    </button>
                </div>
            )}

            {gameState ? (
                <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
                    
                    {/* Players List Sidebar (Always Visible) */}
                    <div style={{ 
                        flex: '1 1 280px', 
                        minWidth: '250px', 
                        border: '1px solid #ccc', 
                        padding: '15px', 
                        borderRadius: '4px',
                        backgroundColor: '#fafafa'
                    }}>
                        <h3 style={{ margin: '0 0 15px 0', borderBottom: '1px solid #eee', paddingBottom: '8px' }}>Players</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                            {gameState.players.map((player) => (
                                <PlayerTile
                                    key={player.id}
                                    player={player}
                                    isCurrentUser={player.display_name === user?.username}
                                    isPlayerHost={player.id === hostPlayerId}
                                    isPlayerActive={player.id === gameState.current_player}
                                    isPlayerNominator={player.id === gameState.last_correct_player}
                                />
                            ))}
                        </div>
                    </div>

                    {/* Active State View Component */}
                    <div style={{ flex: '2 1 500px', minWidth: '300px' }}>
                        {/* Question counter if the game has started */}
                        {gameStarted && (
                            <div style={{ 
                                marginBottom: '15px', 
                                padding: '10px', 
                                backgroundColor: '#e8eaf6', 
                                borderRadius: '4px', 
                                fontWeight: 'bold',
                                color: '#3f51b5',
                                borderLeft: '4px solid #3f51b5'
                            }}>
                                Question {gameState.question_asked_count} of {gameState.total_questions_count}
                            </div>
                        )}
                        {renderActiveView()}
                    </div>

                </div>
            ) : (
                <div style={{ margin: '20px 0', padding: '20px', border: '1px dashed #ccc', textAlign: 'center' }}>
                    <h3>Waiting for Game Snapshot...</h3>
                    <p>Connection established. Awaiting state from the server...</p>
                </div>
            )}
        </div>
    );
}