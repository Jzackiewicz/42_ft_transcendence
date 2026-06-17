import React, { useState } from 'react';
import './Navbar.css';

interface NavbarProps {
    sessionUuid?: string | null;
    actionButtonText: string;
    onActionButtonClick: () => void;
}

export function Navbar({ sessionUuid, actionButtonText, onActionButtonClick }: NavbarProps) {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        if (!sessionUuid) return;
        navigator.clipboard.writeText(sessionUuid);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <nav className="app-nav">
            <div className="app-nav-logo">
                <span className="logo-quiz">QUIZ</span>SENDENCE
            </div>
            
            <div className="app-nav-space" />
            
            {sessionUuid && (
                <div 
                    className={`app-session-code ${copied ? 'copied' : ''}`}
                    onClick={handleCopy}
                    title="Click to copy session code"
                >
                    <span className="code-label">SESSION CODE:</span>
                    <span className="code-value">{sessionUuid}</span>
                    <span className="copy-icon">
                        {copied ? '✓' : '📋'}
                    </span>
                </div>
            )}
            
            <button className="app-nav-btn" onClick={onActionButtonClick}>
                {actionButtonText}
            </button>
        </nav>
    );
}

export default Navbar;
