import { Button } from '../../../../components/Button/Button';
import './LobbyView.css';

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
                            disabled={playersCount < 2 || isGeneratingAiQuestions}
                        >
                            Start Game
                        </Button>

                        <div className="ai-questions-wrapper">
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
                                <span className="ai-feedback-toast">
                                    ✓ AI Questions added to the lobby!
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
