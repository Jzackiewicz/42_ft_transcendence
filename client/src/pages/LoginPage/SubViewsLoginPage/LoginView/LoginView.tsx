import { useState } from 'react'
import { useLoginView } from './useLoginView'
import InputField from '../../../../components/InputField'

function LoginView() {
    const { username, setUsername, password, setPassword, handleLogin } = useLoginView()

    return (
        <div className="login-view">
            <InputField title="Username" type="text" placeholder="Enter your username" value={username} onChange={setUsername} />
            <InputField title="Password" type="password" placeholder="Enter your password" value={password} onChange={setPassword} />
            <button className="auth-submit" onClick={handleLogin}>Sign In ⟶</button>
        </div>
    )
}

export default LoginView;