import React, { useState } from 'react';
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
        setTimeout(() => setCopied(false), 2000);
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
                    <span className={styles['copy-icon']}>
                        {copied ? '✓' : '📋'}
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
