import React from 'react';

export function EvaluationView() {
    return (
        <div style={{ padding: '20px', border: '1px solid #ff9800', borderRadius: '4px', backgroundColor: '#fff3e0' }}>
            <h2>Evaluation Phase</h2>
            <p style={{ fontSize: '16px', color: '#e65100', fontWeight: 'bold' }}>
                🔄 Evaluating answer... Please wait.
            </p>
        </div>
    );
}
