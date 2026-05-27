import { useState } from 'react'
import { useUser } from '../../../../context/UserContext'
import { register, login } from '../../../../api/apiWrapper'

interface RegErrors {
    mailIsEmptyErr?: string
    passIsEmptyErr?: string
    usernameIsEmptyErr?: string
    confirmPassIsEmptyErr?: string

    usernameIsTakenErr?: string
    passWeakErr?: string
    passDoesntMatchErr?: string
    generalErr?: string
}

function matchPass(pass: string, confirmPass: string): boolean {
    if (pass != confirmPass) { return false }
    return true
}

function checkPassStrength(pass: string): boolean {
    if (pass.length < 8) { return false }
    return true
}

function preValidateRegParams(username?: string, mail?: string, pass?: string, confirmPass?: string): RegErrors {

    if (!username) {
        return { usernameIsEmptyErr: "Username is required" }
    }
    if (!mail) {
        return { mailIsEmptyErr: "Mail is required" }
    }
    if (!pass) {
        return { passIsEmptyErr: "Password is required" }
    }
    if (!confirmPass) {
        return { confirmPassIsEmptyErr: "Confirm password is required" }
    }
    
    if (!checkPassStrength(pass)) {
        return { passWeakErr: "pass Is too weak" }
    }
    if (!matchPass(pass, confirmPass)) {
        return { passDoesntMatchErr: "Password & Confirm password must match!" }
    }

    return {}
}

export function useRegistrationView(onSuccess: () => void) {
    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [confPassword, setConfPassword] = useState("")
    const {setUser} = useUser()

    const [errors, setErrors] = useState<RegErrors>({})
    
    
    const handleRegister = async () => {
        const errors = preValidateRegParams(username, email, password, confPassword)
        if (Object.keys(errors).length > 0) {
            setErrors(errors)
            return
        }

        console.log("Registration attempt with:", { username, email })
        try {
            await register(username, email, password)
            const result = await login(username, password)
            if (result) {
                setUser(result)
                onSuccess()
            }
        } catch (error) {
            //internal catch is needed only for proper error displaying
            if (error instanceof Error) {
                try {
                    const parsed = JSON.parse(error.message)
                    setErrors({ generalErr: parsed.detail ?? error.message })
                } catch {
                    setErrors({ generalErr: error.message })
                }
            }
        }
    }

    return { username, setUsername, email, setEmail, password, setPassword, confPassword, setConfPassword, handleRegister, errors }
}