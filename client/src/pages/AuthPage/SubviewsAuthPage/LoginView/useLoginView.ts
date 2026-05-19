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
        console.log("Login attempt with:", { username, password })
        const errs = preValidateLoginParams(username, password)
        // console.log(errs)
        if (errs.usernameErr || errs.passwordErr) { 
            setErrors(errs)
            return 
        }

        try {
            const result = await login(username, password)
            console.log("Login success:", result)
            setUser(result)
            onSuccess()
        } catch (error) {
            console.error("login Err", error)
        }
    }

    return { username, setUsername, password, setPassword, handleLogin, errors }
}