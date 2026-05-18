import { useNavigate } from 'react-router-dom'
import {logout} from '../../api/apiWrapper'
import { useUser } from '../../context/UserContext'


export function useHomePage() {

    const navigate = useNavigate()
    const { user, setUser } = useUser()

    const handleLogout = async () => {
        console.log("logout attempt for user", user?.username)
        try {
            await logout()
            setUser(null)
            navigate('/login')
        } catch (error) {
            console.error("Logout failed:", error)
        }
    }

    return { user, handleLogout } 
}