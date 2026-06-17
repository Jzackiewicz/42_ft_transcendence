import {useState} from 'react'
import {useUser} from '../../../../context/UserContext'
import { login } from '../../../../api/authWrapper'
// import { useNavigate } from 'react-router-dom'

interface LoginErrors {
    usernameErr?: string
    passwordErr?: string
    generalErr?: string
}


function preValidateLoginParams(username?: string, pass?: string): LoginErrors {

    if (!username) {
        return { usernameErr: "Username is required" }
    }
    if (!pass) {
        return { passwordErr: "Password is required" }
    }
    return {}
}

export function useLoginView(onSuccess: () => void) {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const {setUser} = useUser()
    const [errors, setErrors] = useState<LoginErrors>({})


    const handleLogin = async () => {
        const errs = preValidateLoginParams(username, password)
        if (errs.usernameErr || errs.passwordErr) {
            setErrors(errs)
            return
        }

        setErrors({})
        try {
            const result = await login(username, password)
            setUser(result)
            onSuccess()
        } catch (error: any) {
            const data = error?.response?.data
            const message = data?.detail ?? data?.non_field_errors?.[0] ?? error?.message ?? 'Login failed'
            setErrors({ generalErr: message })
        }
    }

    return { username, setUsername, password, setPassword, handleLogin, errors }
}