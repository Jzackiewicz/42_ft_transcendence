import { useState, FormEvent } from 'react';
import { Button } from '../../../../components/Button/Button';
import { Icon } from '../../../../components/Icon/Icon';
import { QuestionBadges } from '../QuestionBadges/QuestionBadges';
import styles from './AnsweringView.module.css';

const ANSWER_MAX_LENGTH = 30;

interface AnsweringViewProps {
    questionText: string;
    category: string;
    isAiGenerated: boolean;
    isVerified: boolean;
    isCurrentAnswering: boolean;
    activePlayerName: string;
    onSubmitAnswer: (answer: string) => void;
}

export function AnsweringView({
    questionText,
    category,
    isAiGenerated,
    isVerified,
    isCurrentAnswering,
    activePlayerName,
    onSubmitAnswer
}: AnsweringViewProps) {
    const [localAnswerText, setLocalAnswerText] = useState('');
    const atLimit = localAnswerText.length >= ANSWER_MAX_LENGTH;
    const isEmpty = localAnswerText.trim() === '';

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (isEmpty) return;
        onSubmitAnswer(localAnswerText);
        setLocalAnswerText('');
    };

    return (
        <div className={styles.answeringViewContainer}>

            <div className={styles.answeringQuestionBox}>
                <div className={styles.answeringQuestionMeta}>
                    <div className={styles.answeringCategory}>
                        Category: {category || 'General'}
                    </div>
                    <QuestionBadges isAiGenerated={isAiGenerated} isVerified={isVerified} />
                </div>
                <div className={styles.answeringQuestionText}>
                    {questionText}
                </div>
            </div>

            {isCurrentAnswering ? (
                <div className={styles.answeringActivePrompt}>
                    <div className={styles.answeringPromptLabel}>
                        YOUR TURN TO ANSWER:
                    </div>
                    <form onSubmit={handleSubmit} className={styles.answeringForm}>
                        <input
                            type="text"
                            value={localAnswerText}
                            onChange={(e) => setLocalAnswerText(e.target.value)}
                            placeholder="Type your answer..."
                            maxLength={ANSWER_MAX_LENGTH}
                            autoFocus
                            className={styles.answeringInput}
                        />
                        <Button type="submit" disabled={isEmpty}>
                            Submit
                        </Button>
                    </form>
                    {atLimit && (
                        <div className={styles.answeringCharLimit}>
                            Character limit reached ({ANSWER_MAX_LENGTH})
                        </div>
                    )}
                </div>
            ) : (
                <div className={styles.answeringSpectatorWaiting}>
                    <Icon name="eye" size="md" /> {activePlayerName} is answering the question...
                </div>
            )}
        </div>
    );
}
