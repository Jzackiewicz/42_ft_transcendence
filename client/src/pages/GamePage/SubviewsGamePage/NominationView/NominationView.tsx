import { Player } from '../../useGamePage';
import styles from './NominationView.module.css';

interface NominationViewProps {
    isCurrentNominator: boolean;
    nominatorName: string;
    eligiblePlayers: Player[];
    onNominatePlayer: (targetPlayerId: number) => void;
}

export function NominationView({
    isCurrentNominator,
    nominatorName
}: NominationViewProps) {
    return (
        <div className={styles.nominationViewContainer}>
            {isCurrentNominator ? (
                <div className={styles.nominationActivePrompt}>
                    <div className={styles.nominationPromptLabel}>
                        👉 Click on any player in the sidebar list to nominate them for the next turn!
                    </div>
                </div>
            ) : (
                <div className={styles.nominationSpectatorWaiting}>
                    👀 {nominatorName} is selecting the next target...
                </div>
            )}
        </div>
    );
}
export default NominationView;

