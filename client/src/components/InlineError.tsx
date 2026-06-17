import './InlineError.css'

interface InlineErrorProps {
    message: string | null
}

function InlineError({ message }: InlineErrorProps) {
    if (!message) return null
    return <span className="inline-error">{message}</span>
}

export default InlineError
