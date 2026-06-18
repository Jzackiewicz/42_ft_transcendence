import React, { useState } from 'react';
import { Button } from '../../../../components/Button/Button';
import './AnsweringView.css';

const ANSWER_MAX_LENGTH = 30;

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
    const atLimit = localAnswerText.length >= ANSWER_MAX_LENGTH;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmitAnswer(localAnswerText);
        setLocalAnswerText('');
    };

    return (
        <div className="answering-view-container">
            
            <div className="answering-question-box">
                <div className="answering-category">
                    Category: {category || 'General'}
                </div>
                <div className="answering-question-text">
                    {questionText}
                </div>
            </div>

            {isCurrentAnswering ? (
                <div className="answering-active-prompt">
                    <div className="answering-prompt-label">
                        YOUR TURN TO ANSWER:
                    </div>
                    <form onSubmit={handleSubmit} className="answering-form">
                        <input
                            type="text"
                            value={localAnswerText}
                            onChange={(e) => setLocalAnswerText(e.target.value)}
                            placeholder="Type your answer..."
                            maxLength={ANSWER_MAX_LENGTH}
                            autoFocus
                            className="answering-input"
                        />
                        <Button type="submit">
                            Submit
                        </Button>
                    </form>
                    {atLimit && (
                        <div className="answering-char-limit">
                            Character limit reached ({ANSWER_MAX_LENGTH})
                        </div>
                    )}
                </div>
            ) : (
                <div className="answering-spectator-waiting">
                    👀 {activePlayerName} is answering the question...
                </div>
            )}
        </div>
    );
}

