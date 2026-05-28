import React, { useState, useEffect } from 'react';
import './LobbySettings.css';

interface LobbySettingsProps {
    isHost: boolean;
    questionCount: number;
    answerTimeLimitMs: number;
    hasBotPlayer: boolean;
    canAddBot: boolean;
    onUpdateSettings: (questions: number, timeLimitSec: number) => void;
    onAddBot: () => void;
    onRemoveBot: () => void;
    onRequestAiQuestions: () => void;
    aiQuestionsRequested: boolean;
}

export function LobbySettings({
    isHost,
    questionCount,
    answerTimeLimitMs,
    hasBotPlayer,
    canAddBot,
    onUpdateSettings,
    onAddBot,
    onRemoveBot,
    onRequestAiQuestions,
    aiQuestionsRequested
}: LobbySettingsProps) {
    const answerTimeLimitSec = Math.round(answerTimeLimitMs / 1000);
    const [aiQuestionsFeedback, setAiQuestionsFeedback] = useState(false);

    useEffect(() => {
        if (aiQuestionsRequested) {
            setAiQuestionsFeedback(true);
            const timer = setTimeout(() => {
                setAiQuestionsFeedback(false);
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [aiQuestionsRequested]);

    const handleQuestionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = parseInt(e.target.value, 10);
        onUpdateSettings(value, answerTimeLimitSec);
    };

    const handleTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = parseInt(e.target.value, 10);
        onUpdateSettings(questionCount, value);
    };

    return (
        <div className="lobby-settings-panel">
            <h3 className="settings-panel-title">
                ⚙️ Lobby Configuration {!isHost && <span className="badge-readonly">🔒 Read-Only</span>}
            </h3>

            {isHost ? (
                <div className="settings-controls-grid">
                    {/* Questions Count Slider */}
                    <div className="setting-control-group">
                        <div className="setting-label-row">
                            <label htmlFor="questions-slider">Questions Limit:</label>
                            <span className="setting-value-badge">{questionCount} questions</span>
                        </div>
                        <input
                            id="questions-slider"
                            type="range"
                            min="10"
                            max="100"
                            step="1"
                            value={questionCount}
                            onChange={handleQuestionChange}
                            className="settings-slider"
                        />
                        <div className="slider-limits">
                            <span>10</span>
                            <span>100</span>
                        </div>
                    </div>

                    {/* Answer Time Limit Slider */}
                    <div className="setting-control-group">
                        <div className="setting-label-row">
                            <label htmlFor="time-slider">Answer Time Limit:</label>
                            <span className="setting-value-badge">{answerTimeLimitSec} seconds</span>
                        </div>
                        <input
                            id="time-slider"
                            type="range"
                            min="5"
                            max="45"
                            step="1"
                            value={answerTimeLimitSec}
                            onChange={handleTimeChange}
                            className="settings-slider"
                        />
                        <div className="slider-limits">
                            <span>5s</span>
                            <span>45s</span>
                        </div>
                    </div>

                    {/* AI Buttons Grid */}
                    <div className="settings-ai-actions">
                        <div className="ai-action-column">
                            <h4 className="ai-section-title">🤖 AI Player</h4>
                            <div className="ai-buttons-row">
                                <button
                                    onClick={onAddBot}
                                    disabled={!canAddBot}
                                    className="btn-settings btn-add-bot"
                                    title={!canAddBot ? "Lobby is full (max 5 players)" : "Add an AI Bot to the lobby"}
                                >
                                    Add AI Bot
                                </button>
                                <button
                                    onClick={onRemoveBot}
                                    disabled={!hasBotPlayer}
                                    className="btn-settings btn-remove-bot"
                                    title={!hasBotPlayer ? "No AI bots in the lobby" : "Remove an AI Bot"}
                                >
                                    Remove AI Bot
                                </button>
                            </div>
                        </div>

                        <div className="ai-action-column">
                            <h4 className="ai-section-title">✨ Question Generation</h4>
                            <button
                                onClick={onRequestAiQuestions}
                                className={`btn-settings btn-generate-questions ${aiQuestionsFeedback ? 'feedback-active' : ''}`}
                            >
                                {aiQuestionsFeedback ? '✨ Generation Requested!' : 'Generate AI Questions'}
                            </button>
                            {aiQuestionsFeedback && (
                                <span className="ai-feedback-toast">
                                    ✓ AI Questions successfully queued for creation!
                                </span>
                            )}
                        </div>
                    </div>
                </div>
            ) : (
                // Guest Read-Only view
                <div className="settings-readonly-view">
                    <div className="readonly-row">
                        <span className="readonly-label">Questions count:</span>
                        <strong className="readonly-value">{questionCount}</strong>
                    </div>
                    <div className="readonly-row">
                        <span className="readonly-label">Answer time limit:</span>
                        <strong className="readonly-value">{answerTimeLimitSec} seconds</strong>
                    </div>
                    <div className="readonly-row">
                        <span className="readonly-label">AI Bots:</span>
                        <strong className={`readonly-value ${hasBotPlayer ? 'text-active' : 'text-inactive'}`}>
                            {hasBotPlayer ? 'Enabled' : 'Disabled'}
                        </strong>
                    </div>
                    <div className="readonly-footer">
                        🔒 Only the lobby host can adjust these room settings.
                    </div>
                </div>
            )}
        </div>
    );
}
