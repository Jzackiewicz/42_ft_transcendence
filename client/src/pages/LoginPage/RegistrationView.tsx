import { useState } from 'react'

import Button from  '../../components/Button'
import InputField from '../../components/InputField'

function RegistrationView() {
    const [displayName, setDisplayName] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")

    return (
        <div className="registration-view">
            <h2>Register</h2>
            <InputField title= "Display Name" type="text" value={displayName} onChange={(value) => setDisplayName(value)} />
            <InputField title="Email" type="email" value={email} onChange={(value) => setEmail(value)} />
            <InputField title="Password" type="password" value={password} onChange={(value) => setPassword(value)} />
            <InputField title="Confirm Password" type="password" value={confirmPassword} onChange={(value) => setConfirmPassword(value)} />
            <button className="auth-submit" onClick={() => {}}> Register </button>
        </div>
    )
}

export default RegistrationView;