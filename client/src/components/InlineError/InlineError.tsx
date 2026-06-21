import styles from './InlineError.module.css'

interface InlineErrorProps {
    message: string | null
}

function InlineError({ message }: InlineErrorProps) {
    if (!message) return null
    return <span className={styles.inlineError}>{message}</span>
}

export default InlineError
