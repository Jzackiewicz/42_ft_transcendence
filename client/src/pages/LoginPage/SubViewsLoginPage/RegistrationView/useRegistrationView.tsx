import {useState} from 'react'
import {register} from '../../../../api/apiWrapper'

export function useRegistrationView() {
    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    
    const handleRegister = async () => {
        console.log("Registration attempt with:", { username, email })
        try {
            await register(username, email, password)
        } catch (error) {
            console.error("Registration failed:", error)
        }
    }

    return { username, setUsername, email, setEmail, password, setPassword, handleRegister }
}