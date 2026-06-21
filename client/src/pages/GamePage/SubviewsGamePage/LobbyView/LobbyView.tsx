import { Button } from '../../../../components/Button/Button';
import { LobbyChat } from '../LobbyChat/LobbyChat';
import styles from './LobbyView.module.css';

interface LobbyViewProps {
    isHost: boolean;
    playersCount: number;
    onStartGame: () => void;
    isGeneratingAiQuestions: boolean;
    aiQuestionsGenerated: boolean;
    onRequestAiQuestions: () => void;
}

export function LobbyView({
    isHost,
    playersCount,
    onStartGame,
    isGeneratingAiQuestions,
    aiQuestionsGenerated,
    onRequestAiQuestions
}: LobbyViewProps) {
    return (
        <div className={styles.lobbyViewContainer}>

            {isHost ? (
                <div>
                    {playersCount < 2 ? (
                        <div className={styles.lobbyWaitingMore}>
                            Waiting for more players to join... (Minimum 2 players required, currently {playersCount})
                        </div>
                    ) : (
                        <div className={styles.lobbyReady}>
                            Ready to start! {playersCount} players in lobby.
                        </div>
                    )}
                    
                    <div className={styles.lobbyActionsRow}>
                        <Button
                            onClick={onStartGame}
                            disabled={playersCount < 2 || isGeneratingAiQuestions}
                        >
                            Start Game
                        </Button>

                        <div className={styles.aiQuestionsWrapper}>
                            <Button
                                onClick={onRequestAiQuestions}
                                disabled={isGeneratingAiQuestions || aiQuestionsGenerated}
                                variant="secondary"
                            >
                                {isGeneratingAiQuestions
                                    ? 'Generating AI Questions…'
                                    : aiQuestionsGenerated
                                        ? 'AI Questions Added'
                                        : 'Generate AI Questions'}
                            </Button>
                            {aiQuestionsGenerated && (
                                <span className={styles.aiFeedbackToast}>
                                    ✓ AI Questions added to the lobby!
                                </span>
                            )}
                        </div>
                    </div>
                </div>
            ) : (
                <div className={styles.lobbySpectatorWaiting}>
                    Waiting for lobby host to start the game...
                </div>
            )}
            <LobbyChat />
        </div>
    );
}
