import { useState } from 'react';
import { Button } from '../Button/Button';
import { Icon } from '../Icon/Icon';
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
        <nav className={styles.appNav}>
            <div className={styles.appNavLogo}>
                <span className={styles.logoQuiz}>QUIZ</span>SCENDENCE
            </div>

            <div className={styles.appNavSpace} />

            {sessionUuid && (
                <div
                    className={cx(styles.appSessionCode, copied && styles.copied)}
                    onClick={handleCopy}
                    title="Click to copy session code"
                >
                    <span className={styles.codeLabel}>SESSION CODE:</span>
                    <span className={styles.codeValue}>{sessionUuid}</span>
                    <span className={styles.copyIcon}>
                        <Icon name={copied ? 'check' : 'copy'} size="sm" />
                    </span>
                </div>
            )}

            <Button onClick={onActionButtonClick} className={styles.navBtn}>
                {actionButtonText}
            </Button>
        </nav>
    );
}

export default Navbar;
