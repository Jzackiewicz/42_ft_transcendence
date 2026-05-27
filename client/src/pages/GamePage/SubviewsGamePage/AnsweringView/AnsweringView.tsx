import React from 'react';
import './AnsweringView.css';

interface AnsweringViewProps {
    questionText: string;
    category: string;
    isCurrentAnswering: boolean;
    activePlayerName: string;
    answerText: string;
    setAnswerText: (val: string) => void;
    onSubmitAnswer: (e: React.FormEvent) => void;
    timeLeft: number | null;
}

export function AnsweringView({
    questionText,
    category,
    isCurrentAnswering,
    activePlayerName,
    answerText,
    setAnswerText,
    onSubmitAnswer,
    timeLeft
}: AnsweringViewProps) {
    return (
        <div className="answering-view-container">
            <h2>Answering Phase</h2>
            
            <div className="answering-question-box">
                <div className="answering-category">
                    Category: {category || 'General'}
                </div>
                <div className="answering-question-text">
                    {questionText}
                </div>
            </div>

            {timeLeft !== null && (
                <div className={`answering-timer ${timeLeft <= 5 ? 'warning' : ''}`}>
                    🕒 Time Left: {timeLeft}s
                </div>
            )}

            {isCurrentAnswering ? (
                <div className="answering-active-prompt">
                    <div className="answering-prompt-label">
                        YOUR TURN TO ANSWER:
                    </div>
                    <form onSubmit={onSubmitAnswer} className="answering-form">
                        <input
                            type="text"
                            value={answerText}
                            onChange={(e) => setAnswerText(e.target.value)}
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

