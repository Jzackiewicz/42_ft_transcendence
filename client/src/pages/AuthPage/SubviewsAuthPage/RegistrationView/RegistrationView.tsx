import { useState } from 'react'
import { useRegistrationView } from './useRegistrationView'
import InputField from '../../../../components/InputField'

interface RegistrationProps {
    onSuccess: () => void
}

function RegistrationView({onSuccess}: RegistrationProps) {
    const { username, setUsername, email, setEmail, password, setPassword, confPassword, setConfPassword, handleRegister, errors } = useRegistrationView(onSuccess)

    return (
        <div className="registration-view">
            <form onSubmit={(e) => {e.preventDefault(); handleRegister()}}> 
                <InputField title= "Display Name" type="text" placeholder="Enter your nickname" value={username} onChange={(value) => setUsername(value)} error={errors.usernameIsEmptyErr} />
                <InputField title="Email" type="email" placeholder="your_email@gmail.com" value={email} onChange={(value) => setEmail(value)} error={errors.mailIsEmptyErr} />
                <InputField title="Password" type="password" placeholder="Create a password" value={password} onChange={(value) => setPassword(value)} error={errors.passIsEmptyErr || errors.passWeakErr} />
                <InputField title="Confirm Password" type="password" placeholder="Confirm your password" value={confPassword} onChange={(value) => setConfPassword(value)} error={errors.confirmPassIsEmptyErr || errors.passDoesntMatchErr} />
                <button type="submit" className="auth-submit"> Register </button>
            </form>
        </div>
    )
}

export default RegistrationView;