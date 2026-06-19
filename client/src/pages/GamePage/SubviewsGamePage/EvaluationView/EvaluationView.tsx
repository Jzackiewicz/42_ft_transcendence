import React from 'react';
import './EvaluationView.css';

interface EvaluationViewProps {
    answerText: string | null;
    correctAnswer: string;
    playerName: string;
    isCorrect: boolean;
    isTimeout: boolean;
    questionText: string;
    category: string;
}

export function EvaluationView({
    answerText,
    correctAnswer,
    playerName,
    isCorrect,
    isTimeout,
    questionText,
    category
}: EvaluationViewProps) {
    let statusClass = 'eval-pending';
    let statusText = '⏳ EVALUATING... (TODO)';

    if (answerText !== '...') {
        if (isCorrect) {
            statusClass = 'eval-correct';
            statusText = '🏆 CORRECT ANSWER';
        } else if (isTimeout) {
            statusClass = 'eval-timeout';
            statusText = "⏰ TIME'S UP";
        } else {
            statusClass = 'eval-wrong';
            statusText = '❌ WRONG ANSWER';
        }
    }

    return (
        <div className={`evaluation-view-container ${statusClass}`}>
            
            <div className="eval-question-info">
                <span className="eval-category">[{category}]</span>
                <p className="eval-question-text">{questionText}</p>
            </div>

            <div className="eval-verdict-title">{statusText}</div>

            <div className="eval-answers-comparison">
                <div className="eval-player-answer-box">
                    <div className="eval-box-label">{playerName}'s Answer:</div>
                    <div className="eval-box-content">
                        {isTimeout ? (
                            <span className="eval-text-none">Timeout</span>
                        ) : (answerText === null || answerText.trim() === '') ? (
                            <span className="eval-text-none">None</span>
                        ) : (
                            <span className="eval-text-value">{answerText}</span>
                        )}
                    </div>
                </div>

                <div className="eval-correct-answer-box">
                    <div className="eval-box-label">Correct Answer:</div>
                    <div className="eval-box-content">
                        <span className="eval-text-value">{correctAnswer}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
