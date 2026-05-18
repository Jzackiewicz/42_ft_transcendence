import { useLoginView } from './useLoginView'
import InputField from '../../../../components/InputField'

interface LoginViewProps {
    onSuccess: () => void
}

function LoginView({ onSuccess }: LoginViewProps) {

    const { username, setUsername, password, setPassword, handleLogin } = useLoginView(onSuccess)

    return (
        <div className="login-view">
            <form onSubmit={(e) => {e.preventDefault(); handleLogin()}}> 
                <InputField title="Username" type="text" placeholder="Enter your username" value={username} onChange={setUsername} />
                <InputField title="Password" type="password" placeholder="Enter your password" value={password} onChange={setPassword} />
                <button type="submit" className="auth-submit">Sign In ⟶</button>
            </form>
        </div>
    )
}

export default LoginView;