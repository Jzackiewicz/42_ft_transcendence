import React, { useState } from 'react';
import './AnsweringView.css';

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
                            autoFocus
                            className="answering-input"
                        />
                        <button type="submit" className="btn-answer-submit">
                            Submit
                        </button>
                    </form>
                </div>
            ) : (
                <div className="answering-spectator-waiting">
                    👀 {activePlayerName} is answering the question...
                </div>
            )}
        </div>
    );
}

