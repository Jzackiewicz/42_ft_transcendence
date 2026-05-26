import React from 'react';

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
        <div style={{ padding: '20px', border: '1px dashed #009688', borderRadius: '4px', backgroundColor: '#f0fdfa' }}>
            <h2>Answering Phase</h2>
            
            <div style={{ margin: '15px 0', padding: '10px', backgroundColor: '#e6fffa', borderLeft: '4px solid #009688' }}>
                <div style={{ fontSize: '12px', textTransform: 'uppercase', color: '#00796b', fontWeight: 'bold' }}>
                    Category: {category || 'General'}
                </div>
                <div style={{ fontSize: '18px', marginTop: '5px', fontWeight: 'bold' }}>
                    {questionText}
                </div>
            </div>

            {timeLeft !== null && (
                <div style={{ 
                    fontSize: '20px', 
                    fontWeight: 'bold', 
                    color: timeLeft <= 5 ? 'red' : 'black',
                    margin: '10px 0' 
                }}>
                    🕒 Time Left: {timeLeft}s
                </div>
            )}

            {isCurrentAnswering ? (
                <div style={{ marginTop: '15px' }}>
                    <div style={{ color: '#00796b', fontWeight: 'bold', marginBottom: '8px' }}>
                        YOUR TURN TO ANSWER:
                    </div>
                    <form onSubmit={onSubmitAnswer} style={{ display: 'flex', gap: '10px' }}>
                        <input
                            type="text"
                            value={answerText}
                            onChange={(e) => setAnswerText(e.target.value)}
                            placeholder="Type your answer..."
                            autoFocus
                            style={{ padding: '8px', fontSize: '16px', flex: 1 }}
                        />
                        <button type="submit" style={{ padding: '8px 16px', fontSize: '16px', cursor: 'pointer' }}>
                            Submit
                        </button>
                    </form>
                </div>
            ) : (
                <div style={{ marginTop: '15px', color: '#666', fontStyle: 'italic' }}>
                    👀 {activePlayerName} is answering the question...
                </div>
            )}
        </div>
    );
}
