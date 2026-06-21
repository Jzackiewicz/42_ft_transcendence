import styles from './ErrorBanner.module.css'

interface ErrorBannerProps {
    message: string | null
    onDismiss: () => void
}

function ErrorBanner({ message, onDismiss }: ErrorBannerProps) {
    if (!message) return null
    return (
        <div className={styles.errorBanner}>
            <span><strong>Error:</strong> {message}</span>
            <button
                onClick={onDismiss}
                className={styles.errorBannerClose}
                aria-label="Dismiss error"
            >
                &times;
            </button>
        </div>
    )
}

export default ErrorBanner
