import {useState} from 'react'
import {useUser} from '../../../../context/UserContext'
import {login} from '../../../../api/apiWrapper'
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
        } catch (error) {
            if (error instanceof Error) {
                setErrors({ generalErr: error.message })
            }
        }
    }

    return { username, setUsername, password, setPassword, handleLogin, errors }
}