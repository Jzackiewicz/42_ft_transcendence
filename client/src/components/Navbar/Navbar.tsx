import { useState } from 'react';
import { Button } from '../Button/Button';
import { cx } from '../../utils/cx';
import styles from './Navbar.module.css';

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
        <nav className={styles['app-nav']}>
            <div className={styles['app-nav-logo']}>
                <span className={styles['logo-quiz']}>QUIZ</span>SENDENCE
            </div>

            <div className={styles['app-nav-space']} />

            {sessionUuid && (
                <div
                    className={cx(styles['app-session-code'], copied && styles.copied)}
                    onClick={handleCopy}
                    title="Click to copy session code"
                >
                    <span className={styles['code-label']}>SESSION CODE:</span>
                    <span className={styles['code-value']}>{sessionUuid}</span>
                    <span className={styles['copy-icon']} aria-hidden="true">
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

            <Button onClick={onActionButtonClick} className={styles['nav-btn']}>
                {actionButtonText}
            </Button>
        </nav>
    );
}

export default Navbar;
