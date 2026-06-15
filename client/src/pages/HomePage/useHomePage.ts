import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createLobby, joinLobby } from '../../api/gameWrapper'
import { logout } from '../../api/authWrapper'
import { useUser } from '../../context/UserContext'

export function useHomePage() {
    const navigate = useNavigate()
    const { user, setUser } = useUser()
    const [joinUuid, setJoinUuid] = useState('')
    const [showJoinModal, setShowJoinModal] = useState(false)

    const handleLogout = async () => {
        try {
            await logout()
            setUser(null)
            navigate('/login')
        } catch (error) {
            console.error('Logout failed:', error)
        }
    }

    const handleCreateLobby = async () => {
        try {
            const data = await createLobby()
            navigate('/lobby', { state: { sessionUuid: data.session_uuid } })
        } catch (error) {
            console.error('Error while creating lobby:', error)
        }
    }

    const handleJoinLobby = async () => {
        if (!joinUuid) return
        try {
            await joinLobby(joinUuid)
            setShowJoinModal(false)
            navigate('/lobby', { state: { sessionUuid: joinUuid } })
        } catch (error) {
            console.error('Error while joining lobby:', error)
        }
    }

    return {
        user,
        handleLogout,
        handleCreateLobby,
        handleJoinLobby,
        joinUuid, setJoinUuid,
        showJoinModal, setShowJoinModal,
    }
}
