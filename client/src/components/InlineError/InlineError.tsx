import styles from './InlineError.module.css'

interface InlineErrorProps {
    message: string | null
}

function InlineError({ message }: InlineErrorProps) {
    if (!message) return null
    return <span className={styles['inline-error']}>{message}</span>
}

export default InlineError
