import {useState} from 'react'
import {useUser} from '../../../../context/UserContext'
import {login} from '../../../../api/apiWrapper'
// import { useNavigate } from 'react-router-dom'

export function useLoginView(onSuccess: () => void) {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")

    const {setUser} = useUser()

    const handleLogin = async () => {
        console.log("Login attempt with:", { username, password })
        try {
            const result = await login(username, password)
            console.log("Login success:", result)
            setUser(result)
            onSuccess()
        } catch (error) {
            console.error("Login failed:", error)
        }
    }

    return { username, setUsername, password, setPassword, handleLogin }
}