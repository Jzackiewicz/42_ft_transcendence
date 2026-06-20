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
        <div className={styles['nomination-view-container']}>
            {isCurrentNominator ? (
                <div className={styles['nomination-active-prompt']}>
                    <div className={styles['nomination-prompt-label']}>
                        👉 Click on any player in the sidebar list to nominate them for the next turn!
                    </div>
                </div>
            ) : (
                <div className={styles['nomination-spectator-waiting']}>
                    👀 {nominatorName} is selecting the next target...
                </div>
            )}
        </div>
    );
}
export default NominationView;

