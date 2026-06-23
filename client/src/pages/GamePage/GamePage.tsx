import { useGamePage } from './useGamePage';
import { GameStatus } from '../../types/Game';
import { useUser } from '../../context/UserContext';
import { FriendsProvider } from '../../context/FriendsListContext';
import { LobbyView } from './SubviewsGamePage/LobbyView/LobbyView';
import { AnsweringView } from './SubviewsGamePage/AnsweringView/AnsweringView';
import { NominationView } from './SubviewsGamePage/NominationView/NominationView';
import { EvaluationView } from './SubviewsGamePage/EvaluationView/EvaluationView';
import { GameOverView } from './SubviewsGamePage/GameOverView/GameOverView';
import { LobbyChat } from './SubviewsGamePage/LobbyChat/LobbyChat';
import { PlayerTile } from './SubviewsGamePage/PlayerTile/PlayerTile';
import { GameHUD } from './SubviewsGamePage/GameHUD/GameHUD';
import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv/BlinkingSpaceBGDiv';
import { Navbar } from '../../components/Navbar/Navbar';
import { Card } from '../../components/Card/Card';
import { SectionTitle } from '../../components/SectionTitle/SectionTitle';
import { Icon } from '../../components/Icon/Icon';
import { cx } from '../../utils/cx';
import { ErrorBanner } from '../../components/ErrorBanner/ErrorBanner';
import styles from './GamePage.module.css';

const phaseClass: Record<GameStatus, string> = {
    [GameStatus.LOBBY]: styles.phaseLobby,
    [GameStatus.ANSWERING]: styles.phaseAnswering,
    [GameStatus.NOMINATION]: styles.phaseNomination,
    [GameStatus.EVALUATION]: styles.phaseEvaluation,
    [GameStatus.GAME_OVER]: styles.phaseGame_over,
};

const phaseTitle: Record<GameStatus, string> = {
    [GameStatus.LOBBY]: 'LOBBY',
    [GameStatus.ANSWERING]: 'ANSWER TO THE QUESTION',
    [GameStatus.NOMINATION]: 'NOMINATE NEXT PLAYER',
    [GameStatus.EVALUATION]: 'ANSWER REVEAL',
    [GameStatus.GAME_OVER]: 'GAME OVER',
};

export function GamePage() {
    return (
        <FriendsProvider>
            <GamePageInner />
        </FriendsProvider>
    );
}

function GamePageInner() {
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
        const { gameState, isHost, currentPlayerObj } = sessionState;
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
    const { gameState, timeLeft, hostPlayerId, isSpectator, currentPlayerObj, eligiblePlayers } = sessionState;

    return (
        <div className={cx(styles.gamePageContainer, gameState && phaseClass[gameState.current_status])}>
            <BlinkingSpaceBGDiv />

            {/* ── Nav ── */}
            <Navbar
                sessionUuid={sessionUuid}
                actionButtonText="Leave Game"
                onActionButtonClick={connection.leaveGame}
            />

            <div className={styles.gamePageContent}>
                {/* Spectator Mode Warning Banner */}
                {isSpectator && (
                    <div className={styles.spectatorBanner}>
                        <Icon name="eye" size="md" /> SPECTATOR MODE — You are watching this match.
                    </div>
                )}

                {errorMsg && (
                    <ErrorBanner
                        message={`Error: ${errorMsg}`}
                        onDismiss={() => setErrorMsg(null)}
                    />
                )}

                {gameState ? (
                    <div className={styles.gameMainLayout}>

                        {/* Players List Sidebar (Always Visible) */}
                        <Card className={styles.gameSidebar}>
                            <SectionTitle as="h3">Players</SectionTitle>
                            <div className={styles.gamePlayersList}>
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
                        </Card>

                        {/* Right column: active game card + lobby chat */}
                        <div className={styles.gameRightColumn}>

                        {/* Active State View Component */}
                        <Card className={styles.gameActiveArea}>
                            <SectionTitle as="h3" className={styles.gameActiveTitle}>
                                {phaseTitle[gameState.current_status]}
                            </SectionTitle>
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
                                    isNomination={gameState.current_status === GameStatus.NOMINATION}
                                />
                            )}
                            {renderActiveView()}
                        </Card>

                        {/* Lobby chat — separate box, lobby phase only */}
                        {gameState.current_status === GameStatus.LOBBY && <LobbyChat />}

                        </div>
                    </div>
                ) : (
                    <div className={styles.gameLoadingBanner}>
                        <h3>Waiting for Game Snapshot...</h3>
                        <p>Connection established. Awaiting state from the server...</p>
                    </div>
                )}
            </div>
        </div>
    );
}