import { useState } from 'react'
import InputField from '../../components/InputField'

function LoginView() {
    const [mail, setMail] = useState("")
    const [password, setPassword] = useState("")
    
    return (
        <div className="login-view">
            <h2>Login</h2>
            <InputField title="Email" type="email" value={mail} onChange={(value) => setMail(value)} />
            <InputField title="Password" type="password" value={password} onChange={(value) => setPassword(value)} />
            <button className="auth-submit" onClick={() => {}} >Sign In ⟶ </button>

        </div>
    )
}

export default LoginView;