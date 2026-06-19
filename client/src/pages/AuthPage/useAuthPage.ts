import { useState } from "react"
import { useNavigate } from 'react-router-dom'


export function useAuthPage() {
    const [isLoginTabActive, setIsLoginTabActive] = useState(true)
    return {isLoginTabActive, setIsLoginTabActive}
}

//navigation for success login
export function useLoginNavigation() {
    const navigate = useNavigate()
    return { onLoginSuccess: () => navigate('/home') }
}

export function useRegistrationNavigation() {
    const navigate = useNavigate()
    return { onRegistrationSuccess: () => navigate('/home')}
}

