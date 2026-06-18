import { useEffect, useState } from 'react'
import { useLoginView } from './useLoginView'
import InputField from '../../../../components/InputField'
import GoogleSignInButton from '../../../../components/GoogleSignInButton'

interface LoginViewProps {
    onSuccess: () => void
}

function LoginView({ onSuccess }: LoginViewProps) {

    const { identifier, setIdentifier, password, setPassword, handleLogin, errors } = useLoginView(onSuccess)

    const [oauthError, setOauthError] = useState<string | null>(null)
    useEffect(() => {
        const params = new URLSearchParams(window.location.search)
        const err = params.get('oauth_error')
        if (err) {
            setOauthError(decodeURIComponent(err))
            // Remove the query string from the URL without reloading.
            const url = new URL(window.location.href)
            url.searchParams.delete('oauth_error')
            window.history.replaceState({}, '', url.toString())
        }
    }, [])

    return (
        <div className="login-view">
            <form onSubmit={(e) => {e.preventDefault(); handleLogin()}}>
                <InputField title="Email or username" type="text" placeholder="Enter your email or username" value={identifier} onChange={setIdentifier} error={errors.identifierErr} />
                <InputField title="Password" type="password" placeholder="Enter your password" value={password} onChange={setPassword} error={errors.passwordErr}/>
                {errors.generalErr && <span className="form-error">{errors.generalErr}</span>}
                {oauthError && <span className="form-error">Google sign-in failed: {oauthError}</span>}
                <button type="submit" className="auth-submit">Sign In ⟶</button>
                <div className="auth-divider">or</div>
                <GoogleSignInButton label="Sign in with Google" />
            </form>
        </div>
    )
}

export default LoginView;
