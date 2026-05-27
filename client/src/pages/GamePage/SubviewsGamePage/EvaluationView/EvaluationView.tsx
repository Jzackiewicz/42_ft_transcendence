import React from 'react';
import './EvaluationView.css';

export function EvaluationView() {
    return (
        <div className="evaluation-view-container">
            <h2>Evaluation Phase</h2>
            <p className="evaluation-loading-text">
                🔄 Evaluating answer... Please wait.
            </p>
        </div>
    );
}

