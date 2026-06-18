import {useState} from 'react'
import {useUser} from '../../../../context/UserContext'
import { login } from '../../../../api/authWrapper'
// import { useNavigate } from 'react-router-dom'

interface LoginErrors {
    identifierErr?: string
    passwordErr?: string
    generalErr?: string
}


function preValidateLoginParams(identifier?: string, pass?: string): LoginErrors {

    if (!identifier) {
        return { identifierErr: "Email or username is required" }
    }
    if (!pass) {
        return { passwordErr: "Password is required" }
    }
    return {}
}

export function useLoginView(onSuccess: () => void) {
    const [identifier, setIdentifier] = useState("")
    const [password, setPassword] = useState("")
    const {setUser} = useUser()
    const [errors, setErrors] = useState<LoginErrors>({})


    const handleLogin = async () => {
        const errs = preValidateLoginParams(identifier, password)
        if (errs.identifierErr || errs.passwordErr) {
            setErrors(errs)
            return
        }

        setErrors({})
        try {
            const result = await login(identifier.trim(), password)
            setUser(result)
            onSuccess()
        } catch (error: any) {
            const data = error?.response?.data
            const message = data?.detail ?? data?.non_field_errors?.[0] ?? error?.message ?? 'Login failed'
            setErrors({ generalErr: message })
        }
    }

    return { identifier, setIdentifier, password, setPassword, handleLogin, errors }
}
