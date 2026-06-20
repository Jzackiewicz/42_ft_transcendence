import React, { useState } from 'react';
import { Button } from '../../../../components/Button/Button';
import styles from './AnsweringView.module.css';

interface AnsweringViewProps {
    questionText: string;
    category: string;
    isCurrentAnswering: boolean;
    activePlayerName: string;
    onSubmitAnswer: (answer: string) => void;
}

export function AnsweringView({
    questionText,
    category,
    isCurrentAnswering,
    activePlayerName,
    onSubmitAnswer
}: AnsweringViewProps) {
    const [localAnswerText, setLocalAnswerText] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmitAnswer(localAnswerText);
        setLocalAnswerText('');
    };

    return (
        <div className={styles['answering-view-container']}>

            <div className={styles['answering-question-box']}>
                <div className={styles['answering-category']}>
                    Category: {category || 'General'}
                </div>
                <div className={styles['answering-question-text']}>
                    {questionText}
                </div>
            </div>

            {isCurrentAnswering ? (
                <div className={styles['answering-active-prompt']}>
                    <div className={styles['answering-prompt-label']}>
                        YOUR TURN TO ANSWER:
                    </div>
                    <form onSubmit={handleSubmit} className={styles['answering-form']}>
                        <input
                            type="text"
                            value={localAnswerText}
                            onChange={(e) => setLocalAnswerText(e.target.value)}
                            placeholder="Type your answer..."
                            autoFocus
                            className={styles['answering-input']}
                        />
                        <Button type="submit">
                            Submit
                        </Button>
                    </form>
                </div>
            ) : (
                <div className={styles['answering-spectator-waiting']}>
                    👀 {activePlayerName} is answering the question...
                </div>
            )}
        </div>
    );
}

