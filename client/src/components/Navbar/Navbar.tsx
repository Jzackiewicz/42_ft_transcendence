import { useState } from 'react';
import { Button } from '../Button/Button';
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
        setTimeout(() => setCopied(false), 1500);
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
                    <span className="copy-icon" aria-hidden="true">
                        {copied ? (
                            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                                <path d="M3 8.5L6.5 12L13 4.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                        ) : (
                            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                                <rect x="5" y="5" width="9" height="9" rx="1.5" stroke="currentColor" strokeWidth="1.6"/>
                                <path d="M3 11V3.5C3 2.67 3.67 2 4.5 2H11" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
                            </svg>
                        )}
                    </span>
                </div>
            )}

            <Button onClick={onActionButtonClick}>
                {actionButtonText}
            </Button>
        </nav>
    );
}

export default Navbar;
