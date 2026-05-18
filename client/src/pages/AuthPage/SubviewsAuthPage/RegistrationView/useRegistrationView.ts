import { useState } from 'react'
import {useUser} from '../../../../context/UserContext'
import { register, login } from '../../../../api/apiWrapper'


export function useRegistrationView(onSuccess: () => void) {
    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")

    const {setUser} = useUser()
    
    const handleRegister = async () => {
        console.log("Registration attempt with:", { username, email })
        try {
            await register(username, email, password)
            const result = await login(username, password)
            if (result) {
                setUser(result)
                onSuccess()
            }
        } catch (error) {
            console.error("Registration failed:", error)
        }
    }

    return { username, setUsername, email, setEmail, password, setPassword, handleRegister }
}