import { Icon } from '../../../../components/Icon/Icon';
import styles from './NominationView.module.css';

interface NominationViewProps {
    isCurrentNominator: boolean;
    nominatorName: string;
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
                        <Icon name="arrowRight" size="md" /> Click on any player in the sidebar list to nominate them for the next turn!
                    </div>
                </div>
            ) : (
                <div className={styles.nominationSpectatorWaiting}>
                    <Icon name="eye" size="md" /> {nominatorName} is selecting the next target...
                </div>
            )}
        </div>
    );
}

