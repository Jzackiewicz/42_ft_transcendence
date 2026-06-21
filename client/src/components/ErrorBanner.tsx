import './ErrorBanner.css'

interface ErrorBannerProps {
    message: string | null
    onDismiss: () => void
}

function ErrorBanner({ message, onDismiss }: ErrorBannerProps) {
    if (!message) return null
    return (
        <div className="error-banner">
            <span><strong>Error:</strong> {message}</span>
            <button
                onClick={onDismiss}
                className="error-banner-close"
                aria-label="Dismiss error"
            >
                &times;
            </button>
        </div>
    )
}

export default ErrorBanner
