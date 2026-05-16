import { useEffect, useState } from "react"
import { initCSRF } from "../../api/apiWrapper"
import { useNavigate } from 'react-router-dom'


export function useAuthPage() {
    const [isLoginTabActive, setIsLoginTabActive] = useState(true)
    useEffect(() => { 
            console.log("Initializing CSRF...")
            initCSRF()
                .catch(err => console.error("CSRF failed:", err))
        }, [])

    return {isLoginTabActive, setIsLoginTabActive}
}

//navigation for success login
export function useLoginNavigation() {
    const navigate = useNavigate()
    return { onLoginSuccess: () => navigate('/home') }
}
