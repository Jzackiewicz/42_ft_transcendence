import { Badge } from '../../../../components/Badge/Badge';
import styles from './QuestionBadges.module.css';

interface QuestionBadgesProps {
    isAiGenerated: boolean;
    isVerified: boolean;
}

export function QuestionBadges({ isAiGenerated, isVerified }: QuestionBadgesProps) {
    if (!isAiGenerated && !isVerified) {
        return null;
    }

    return (
        <span className={styles['question-badges']}>
            {isAiGenerated && (
                <Badge variant="ai" title="AI generated question">
                    AI Generated
                </Badge>
            )}
            {isVerified && (
                <Badge variant="verified" title="Verified question">
                    Verified
                </Badge>
            )}
        </span>
    );
}
