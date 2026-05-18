import { useState } from 'react'
import { useRegistrationView } from './useRegistrationView'
import InputField from '../../../../components/InputField'

interface RegistrationProps {
    onSuccess: () => void
}

function RegistrationView({onSuccess}: RegistrationProps) {
    const { username, setUsername, email, setEmail, password, setPassword, handleRegister } = useRegistrationView(onSuccess)
    const [confirmPassword, setConfirmPassword] = useState("")

    return (
        <div className="registration-view">
            <h2>Register</h2>
            <InputField title= "Display Name" type="text" placeholder="Enter your nickname" value={username} onChange={(value) => setUsername(value)} />
            <InputField title="Email" type="email" placeholder="your_email@gmail.com" value={email} onChange={(value) => setEmail(value)} />
            <InputField title="Password" type="password" placeholder="Create a password" value={password} onChange={(value) => setPassword(value)} />
            <InputField title="Confirm Password" type="password" placeholder="Confirm your password" value={confirmPassword} onChange={(value) => setConfirmPassword(value)} />
            <button className="auth-submit" onClick={handleRegister}> Register </button>
        </div>
    )
}

export default RegistrationView;