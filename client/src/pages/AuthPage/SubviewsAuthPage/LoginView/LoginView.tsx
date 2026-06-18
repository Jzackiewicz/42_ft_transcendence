import { useLoginView } from './useLoginView'
import InputField from '../../../../components/InputField'

interface LoginViewProps {
    onSuccess: () => void
}

function LoginView({ onSuccess }: LoginViewProps) {

    const { identifier, setIdentifier, password, setPassword, handleLogin, errors } = useLoginView(onSuccess)

    return (
        <div className="login-view">
            <form onSubmit={(e) => {e.preventDefault(); handleLogin()}}>
                <InputField title="Email or username" type="text" placeholder="Enter your email or username" value={identifier} onChange={setIdentifier} error={errors.identifierErr} />
                <InputField title="Password" type="password" placeholder="Enter your password" value={password} onChange={setPassword} error={errors.passwordErr}/>
                {errors.generalErr && <span className="form-error">{errors.generalErr}</span>}
                <button type="submit" className="auth-submit">Sign In ⟶</button>
            </form>
        </div>
    )
}

export default LoginView;
