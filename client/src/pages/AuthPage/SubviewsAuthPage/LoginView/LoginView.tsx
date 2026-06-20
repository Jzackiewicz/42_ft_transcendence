import { useEffect, useState } from 'react'
import { useLoginView } from './useLoginView'
import InputField from '../../../../components/InputField'
import InlineError from '../../../../components/InlineError'
import GoogleSignInButton from '../../../../components/GoogleSignInButton'

interface LoginViewProps {
    onSuccess: () => void
}

const OAUTH_ERROR_MESSAGES: Record<string, string> = {
    cancelled: 'Google sign in was cancelled',
    missing_params: 'Sign in link was invalid. Please try again',
    invalid_state: 'Sign in link expired. Please try again',
    state_mismatch: 'Sign in link was invalid. Please try again',
    email_not_verified: 'Please verify your email with Google before signing in',
    exchange_failed: "Couldn't reach Google. Please try again",
    server_error: 'Something went wrong. Please try again',
}


const OAUTH_ERROR_TIMEOUT_MS = 8000

function LoginView({ onSuccess }: LoginViewProps) {

    const { identifier, setIdentifier, password, setPassword, handleLogin, errors } = useLoginView(onSuccess)

    const [oauthError, setOauthError] = useState<string | null>(null)
    useEffect(() => {
        const params = new URLSearchParams(window.location.search)
        const code = params.get('oauth_error')
        if (!code) return

        setOauthError(OAUTH_ERROR_MESSAGES[code] ?? OAUTH_ERROR_MESSAGES.server_error)

        const url = new URL(window.location.href)
        url.searchParams.delete('oauth_error')
        window.history.replaceState({}, '', url.toString())

        const timer = setTimeout(() => setOauthError(null), OAUTH_ERROR_TIMEOUT_MS)
        return () => clearTimeout(timer)
    }, [])


    const dismissOauthError = () => {
        if (oauthError) setOauthError(null)
    }

    return (
        <div className="login-view">
            <form onSubmit={(e) => {e.preventDefault(); dismissOauthError(); handleLogin()}}>
                <InputField title="Email or username" type="text" placeholder="Enter your email or username" value={identifier} onChange={(v) => { dismissOauthError(); setIdentifier(v) }} error={errors.identifierErr} />
                <InputField title="Password" type="password" placeholder="Enter your password" value={password} onChange={(v) => { dismissOauthError(); setPassword(v) }} error={errors.passwordErr}/>
                <InlineError message={oauthError ?? errors.generalErr ?? null} />
                <button type="submit" className="auth-submit">Sign In ⟶</button>
                <div className="auth-divider">or</div>
                <div onClick={dismissOauthError}>
                    <GoogleSignInButton label="Sign in with Google" />
                </div>
            </form>
        </div>
    )
}

export default LoginView;
