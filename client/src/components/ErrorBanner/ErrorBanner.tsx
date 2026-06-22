import styles from './ErrorBanner.module.css';
import { cx } from '../../utils/cx';

interface ErrorBannerProps {
    message: string;
    onDismiss?: () => void;
    action?: React.ReactNode;
    className?: string;
}

export function ErrorBanner({ message, onDismiss, action, className }: ErrorBannerProps) {
    return (
        <div className={cx(styles.errorBanner, className)} role="alert">
            <span>{message}</span>
            {action}
            {onDismiss && (
                <button
                    className={styles.errorBannerDismiss}
                    onClick={onDismiss}
                    aria-label="Dismiss error"
                >
                    &times;
                </button>
            )}
        </div>
    );
}

export default ErrorBanner;
