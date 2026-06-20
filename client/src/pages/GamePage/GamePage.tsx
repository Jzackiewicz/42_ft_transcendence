import React from 'react';
import { useGamePage, GameStatus } from './useGamePage';
import { useUser } from '../../context/UserContext';
import { LobbyView } from './SubviewsGamePage/LobbyView/LobbyView';
import { AnsweringView } from './SubviewsGamePage/AnsweringView/AnsweringView';
import { NominationView } from './SubviewsGamePage/NominationView/NominationView';
import { EvaluationView } from './SubviewsGamePage/EvaluationView/EvaluationView';
import { GameOverView } from './SubviewsGamePage/GameOverView/GameOverView';
import { PlayerTile } from './SubviewsGamePage/PlayerTile/PlayerTile';
import { GameHUD } from './SubviewsGamePage/GameHUD/GameHUD';
import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv';
import { Navbar } from '../../components/Navbar/Navbar';
import './GamePage.css';

export function GamePage() {
    const { user } = useUser();

    const {
        connection,
        gameActions,
        sessionState,
        isGeneratingAiQuestions,
        aiQuestionsGenerated,
        onRequestAiQuestions
    } = useGamePage();

    // Dynamic game states renderer
    const renderActiveView = () => {
        const { gameState, isHost, currentPlayerObj, eligiblePlayers } = sessionState;
        if (!gameState) return null;

        switch (gameState.current_status) {
            case GameStatus.LOBBY: {
                return (
                    <LobbyView
                        isHost={isHost}
                        playersCount={gameState.players.length}
                        onStartGame={gameActions.startGame}
                        isGeneratingAiQuestions={isGeneratingAiQuestions}
                        aiQuestionsGenerated={aiQuestionsGenerated}
                        onRequestAiQuestions={onRequestAiQuestions}
                    />
                );
            }
            case GameStatus.ANSWERING: {
                return (
                    <AnsweringView
                        questionText={gameState.current_question?.question?.question_text || ''}
                        category={gameState.current_question?.question?.category || ''}
                        isAiGenerated={gameState.current_question?.question?.is_ai_generated ?? false}
                        isVerified={gameState.current_question?.question?.is_verified ?? false}
                        isCurrentAnswering={gameState.current_player === currentPlayerObj?.id}
                        activePlayerName={gameState.players.find(p => p.id === gameState.current_player)?.display_name || 'Someone'}
                        onSubmitAnswer={gameActions.submitAnswer}
                    />
                );
            }
            case GameStatus.NOMINATION: {
                return (
                    <NominationView
                        isCurrentNominator={gameState.last_correct_player === currentPlayerObj?.id}
                        nominatorName={gameState.players.find(p => p.id === gameState.last_correct_player)?.display_name || 'Someone'}
                        eligiblePlayers={eligiblePlayers}
                        onNominatePlayer={gameActions.nominatePlayer}
                    />
                );
            }
            case GameStatus.EVALUATION: {
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
                        isAiGenerated={gameState.current_question?.question?.is_ai_generated ?? false}
                        isVerified={gameState.current_question?.question?.is_verified ?? false}
                    />
                );
            }
            case GameStatus.GAME_OVER: {
                return (
                    <GameOverView
                        winnerId={gameState.winner}
                        winnerName={gameState.players.find(p => p.id === gameState.winner)?.display_name || ''}
                        endReason={gameState.end_reason || ''}
                        players={gameState.players}
                        onReturnToHome={connection.leaveGame}
                    />
                );
            }
            default: {
                return (
                    <div>
                        Unknown game status: {gameState.current_status}
                    </div>
                );
            }
        }
    };

    const { sessionUuid, errorMsg, setErrorMsg } = connection;
    const { gameState, gameStarted, timeLeft, hostPlayerId, isSpectator, currentPlayerObj, eligiblePlayers } = sessionState;

    return (
        <div className={`game-page-container phase-${gameState?.current_status || 'none'}`}>
            <BlinkingSpaceBGDiv />

            {/* ── Nav ── */}
            <Navbar
                sessionUuid={sessionUuid}
                actionButtonText="Leave Game"
                onActionButtonClick={connection.leaveGame}
            />

            <div className="game-page-content">
                {/* Spectator Mode Warning Banner */}
                {isSpectator && (
                    <div className="spectator-banner">
                        👁️ SPECTATOR MODE — You are watching this match.
                    </div>
                )}

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
                        <div className="game-sidebar section-card">
                            <h3 className="game-sidebar-title section-title">Players</h3>
                            <div className="game-players-list">
                                {gameState.players.map((player) => {
                                    const isCurrentNominator = gameState.last_correct_player === currentPlayerObj?.id;
                                    const isInNominationPhase = gameState.current_status === GameStatus.NOMINATION;
                                    const isEligible = eligiblePlayers.some(p => p.id === player.id);
                                    const isClickable = isInNominationPhase && isCurrentNominator && isEligible;

                                    return (
                                        <PlayerTile
                                            key={player.id}
                                            player={player}
                                            isCurrentUser={player.id === currentPlayerObj?.id || (player.user_id !== null && player.user_id !== undefined && player.user_id === user?.id)}
                                            isPlayerHost={player.id === hostPlayerId}
                                            isPlayerActive={player.id === gameState.current_player}
                                            isPlayerNominator={player.id === gameState.last_correct_player}
                                            isClickable={isClickable}
                                            onClick={() => gameActions.nominatePlayer(player.id)}
                                        />
                                    );
                                })}
                            </div>
                        </div>

                        {/* Active State View Component */}
                        <div className="game-active-area section-card">
                            <h3 className="game-active-title section-title">
                                {gameState.current_status === GameStatus.LOBBY && "LOBBY"}
                                {gameState.current_status === GameStatus.ANSWERING && "ANSWER TO THE QUESTION"}
                                {gameState.current_status === GameStatus.NOMINATION && "NOMINATE NEXT PLAYER"}
                                {gameState.current_status === GameStatus.EVALUATION && "ANSWER REVEAL"}
                                {gameState.current_status === GameStatus.GAME_OVER && "GAME OVER"}
                            </h3>
                            {/* Question & Timer HUD */}
                            {gameState.current_status !== GameStatus.GAME_OVER && (
                                <GameHUD
                                    questionAskedCount={gameState.question_asked_count}
                                    totalQuestionsCount={gameState.total_questions_count}
                                    generatedQuestionsCount={gameState.generated_questions_count}
                                    timeLeft={timeLeft}
                                    timeLimitSeconds={gameState.answer_time_limit_ms / 1000}
                                    nominationTimeLimitSeconds={gameState.nomination_time_limit_ms / 1000}
                                    maxPlayers={gameState.max_players}
                                    isLobby={gameState.current_status === GameStatus.LOBBY}
                                    isEvaluation={gameState.current_status === GameStatus.EVALUATION}
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
        </div>
    );
}