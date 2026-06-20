import { cx } from '../../../../utils/cx';
import { QuestionBadges } from '../QuestionBadges/QuestionBadges';
import styles from './EvaluationView.module.css';

interface EvaluationViewProps {
    answerText: string | null;
    correctAnswer: string;
    playerName: string;
    isCorrect: boolean;
    isTimeout: boolean;
    questionText: string;
    category: string;
    isAiGenerated: boolean;
    isVerified: boolean;
}

export function EvaluationView({
    answerText,
    correctAnswer,
    playerName,
    isCorrect,
    isTimeout,
    questionText,
    category,
    isAiGenerated,
    isVerified
}: EvaluationViewProps) {
    let statusClass = '';
    let statusText = '';
    if (isCorrect) {
        statusClass = styles['eval-correct'];
        statusText = '🏆 CORRECT ANSWER';
    } else if (isTimeout) {
        statusClass = styles['eval-timeout'];
        statusText = "⏰ TIME'S UP";
    } else {
        statusClass = styles['eval-wrong'];
        statusText = '❌ WRONG ANSWER';
    }

    return (
        <div className={cx(styles['evaluation-view-container'], statusClass)}>
            
            <div className={styles['eval-question-info']}>
                <div className={styles['eval-question-meta']}>
                    <span className={styles['eval-category']}>[{category}]</span>
                    <QuestionBadges isAiGenerated={isAiGenerated} isVerified={isVerified} />
                </div>
                <p className={styles['eval-question-text']}>{questionText}</p>
            </div>

            <div className={styles['eval-verdict-title']}>{statusText}</div>

            <div className={styles['eval-answers-comparison']}>
                <div className={styles['eval-player-answer-box']}>
                    <div className={styles['eval-box-label']}>{playerName}'s Answer:</div>
                    <div className={styles['eval-box-content']}>
                        {isTimeout ? (
                            <span className={styles['eval-text-none']}>Timeout</span>
                        ) : (answerText === null || answerText.trim() === '') ? (
                            <span className={styles['eval-text-none']}>None</span>
                        ) : (
                            <span className={styles['eval-text-value']}>{answerText}</span>
                        )}
                    </div>
                </div>

                <div className={styles['eval-correct-answer-box']}>
                    <div className={styles['eval-box-label']}>Correct Answer:</div>
                    <div className={styles['eval-box-content']}>
                        <span className={styles['eval-text-value']}>{correctAnswer}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
