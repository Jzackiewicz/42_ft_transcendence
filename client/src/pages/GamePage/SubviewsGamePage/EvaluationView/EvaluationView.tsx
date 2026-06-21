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
        statusClass = styles.evalCorrect;
        statusText = '🏆 CORRECT ANSWER';
    } else if (isTimeout) {
        statusClass = styles.evalTimeout;
        statusText = "⏰ TIME'S UP";
    } else {
        statusClass = styles.evalWrong;
        statusText = '❌ WRONG ANSWER';
    }

    return (
        <div className={cx(styles.evaluationViewContainer, statusClass)}>
            
            <div className={styles.evalQuestionInfo}>
                <div className={styles.evalQuestionMeta}>
                    <span className={styles.evalCategory}>[{category}]</span>
                    <QuestionBadges isAiGenerated={isAiGenerated} isVerified={isVerified} />
                </div>
                <p className={styles.evalQuestionText}>{questionText}</p>
            </div>

            <div className={styles.evalVerdictTitle}>{statusText}</div>

            <div className={styles.evalAnswersComparison}>
                <div className={styles.evalPlayerAnswerBox}>
                    <div className={styles.evalBoxLabel}>{playerName}'s Answer:</div>
                    <div className={styles.evalBoxContent}>
                        {isTimeout ? (
                            <span className={styles.evalTextNone}>Timeout</span>
                        ) : (answerText === null || answerText.trim() === '') ? (
                            <span className={styles.evalTextNone}>None</span>
                        ) : (
                            <span className={styles.evalTextValue}>{answerText}</span>
                        )}
                    </div>
                </div>

                <div className={styles.evalCorrectAnswerBox}>
                    <div className={styles.evalBoxLabel}>Correct Answer:</div>
                    <div className={styles.evalBoxContent}>
                        <span className={styles.evalTextValue}>{correctAnswer}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
