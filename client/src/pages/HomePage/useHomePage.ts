import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createLobby, joinLobby } from '../../api/gameWrapper'
import { logout } from '../../api/authWrapper'
import { useUser } from '../../context/UserContext'

export function useHomePage() {
    const navigate = useNavigate()
    const { user, setUser: setUserCtx } = useUser()
    const [joinUuid, setJoinUuid] = useState('')
    const [showJoinModal, setShowJoinModal] = useState(false)

    const handleLogout = async () => {
        try {
            await logout()
            setUserCtx(null)
            navigate('/login')
        } catch (error: any) {
            navigate('/error', { state: {
                code: error?.response?.status ?? 500,
                message: 'Logout failed. Please try again.',
            }})
        }
    }

    const handleCreateLobby = async () => {
        try {
            const data = await createLobby()
            navigate('/lobby', { state: { sessionUuid: data.session_uuid } })
        } catch (error: any) {
            navigate('/error', { state: {
                code: error?.response?.status ?? 500,
                message: 'Failed to create a lobby. Please try again.',
            }})
        }
    }

    const handleJoinLobby = async () => {
        if (!joinUuid) return
        try {
            await joinLobby(joinUuid)
            setShowJoinModal(false)
            navigate('/lobby', { state: { sessionUuid: joinUuid } })
        } catch (error: any) {
            const message = error?.response?.data?.error?.[0]
                ?? error?.response?.data?.detail
                ?? 'Failed to join lobby. Check the UUID and try again.'
            navigate('/error', { state: {
                code: error?.response?.status ?? 500,
                message,
            }})
        }
    }

    return {
        user,
        setUser: setUserCtx,
        handleLogout,
        handleCreateLobby,
        handleJoinLobby,
        joinUuid, setJoinUuid,
        showJoinModal, setShowJoinModal,
    }
}
