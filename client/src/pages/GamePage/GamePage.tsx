import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useGamePage, GameStatus } from './useGamePage';
import { useUser } from '../../context/UserContext';
import { LobbyView } from './SubviewsGamePage/LobbyView/LobbyView';
import { AnsweringView } from './SubviewsGamePage/AnsweringView/AnsweringView';
import { NominationView } from './SubviewsGamePage/NominationView/NominationView';
import { EvaluationView } from './SubviewsGamePage/EvaluationView/EvaluationView';
import { GameOverView } from './SubviewsGamePage/GameOverView/GameOverView';
import { PlayerTile } from './SubviewsGamePage/PlayerTile/PlayerTile';
import { GameHUD } from './SubviewsGamePage/GameHUD/GameHUD';
import './GamePage.css';

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
        isGameOver,
        questionCount,
        answerTimeLimitMs,
        aiQuestionsRequested,
        updateSettings,
        addAiBot,
        removeAiBot,
        requestAiQuestions
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

    // Dynamic game states renderer
    const renderActiveView = () => {
        if (!gameState) return null;

        switch (gameState.current_status) {
            case GameStatus.LOBBY:
                return (
                    <LobbyView 
                        isHost={isHost}
                        playersCount={gameState.players.length}
                        onStartGame={startGame}
                        questionCount={questionCount}
                        answerTimeLimitMs={answerTimeLimitMs}
                        hasBotPlayer={gameState.players.some(p => p.player_type === 'bot')}
                        canAddBot={gameState.players.length < 5}
                        onUpdateSettings={updateSettings}
                        onAddBot={addAiBot}
                        onRemoveBot={removeAiBot}
                        onRequestAiQuestions={requestAiQuestions}
                        aiQuestionsRequested={aiQuestionsRequested}
                    />
                );
            case GameStatus.ANSWERING:
                return (
                    <AnsweringView 
                        questionText={gameState.current_question?.question?.question_text || ''}
                        category={gameState.current_question?.question?.category || ''}
                        isCurrentAnswering={gameState.current_player === currentPlayerObj?.id}
                        activePlayerName={gameState.players.find(p => p.id === gameState.current_player)?.display_name || 'Someone'}
                        answerText={answerText}
                        setAnswerText={setAnswerText}
                        onSubmitAnswer={handleAnswerSubmit}
                    />
                );
            case GameStatus.NOMINATION:
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
            case GameStatus.EVALUATION:
                const attempt = gameState.current_attempt;
                const activePlayer = gameState.players.find(p => p.id === attempt?.player);
                return (
                    <EvaluationView 
                        answerText={attempt?.answer_text || null}
                        correctAnswer={attempt?.correct_answer || ''}
                        playerName={activePlayer?.display_name || 'Unknown'}
                        isCorrect={attempt?.is_correct || false}
                        isTimeout={attempt?.is_timeout || false}
                        questionText={gameState.current_question?.question?.question_text || ''}
                        category={gameState.current_question?.question?.category || ''}
                    />
                );
            case GameStatus.GAME_OVER:
                return (
                    <GameOverView 
                        winnerId={gameState.winner}
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

    return (
        <div className="game-page-container">
            {/* Top Bar (Session Code & Leave Button) */}
            <div className="game-top-bar">
                <h1>Quizscendence</h1>
                <div className="game-top-bar-right">
                    <div><strong>SESSION CODE:</strong> {sessionUuid || 'None'}</div>
                    <button onClick={handleLeave} className="btn-leave">Leave Game</button>
                </div>
            </div>

            {/* Error Banner */}
            {errorMsg && (
                <div className="game-error-banner">
                    <span><strong>Error:</strong> {errorMsg}</span>
                    <button 
                        onClick={() => setErrorMsg(null)} 
                        className="btn-error-close"
                    >
                        &times;
                    </button>
                </div>
            )}

            {gameState ? (
                <div className="game-main-layout">
                    
                    {/* Players List Sidebar (Always Visible) */}
                    <div className="game-sidebar">
                        <h3 className="game-sidebar-title">Players</h3>
                        <div className="game-players-list">
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
                    <div className="game-active-area">
                        {/* Question & Timer HUD if the game has started */}
                        {gameStarted && (
                            <GameHUD
                                questionAskedCount={gameState.question_asked_count}
                                totalQuestionsCount={gameState.total_questions_count}
                                timeLeft={timeLeft}
                            />
                        )}
                        {renderActiveView()}
                    </div>

                </div>
            ) : (
                <div className="game-loading-banner">
                    <h3>Waiting for Game Snapshot...</h3>
                    <p>Connection established. Awaiting state from the server...</p>
                </div>
            )}
        </div>
    );
}