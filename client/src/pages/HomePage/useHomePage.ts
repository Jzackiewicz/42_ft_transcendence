import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createLobby, joinLobby } from '../../api/gameWrapper'
import { logout } from '../../api/authWrapper'
import { useUser } from '../../context/UserContext'

// A UUID is 36 characters (8-4-4-4-12 plus four hyphens).
export const UUID_LENGTH = 36

export function useHomePage() {
    const navigate = useNavigate()
    const { user, setUser: setUserCtx, setActiveSessionUuid } = useUser()
    const [joinUuid, setJoinUuid] = useState('')
    const [joinError, setJoinError] = useState<string | null>(null)
    const [createError, setCreateError] = useState<string | null>(null)
    const [showJoinModal, setShowJoinModal] = useState(false)
    const [showRulesModal, setShowRulesModal] = useState(false)

    const openJoinModal = (open: boolean) => {
        setJoinError(null)
        setShowJoinModal(open)
    }

    const handleLogout = async () => {
        try {
            await logout()
            setUserCtx(null)
            setActiveSessionUuid(null)
            navigate('/login')
        } catch (error: any) {
            navigate('/error', { state: {
                code: error?.response?.status ?? 500,
                message: 'Logout failed. Please try again.',
            }})
        }
    }

    const extractError = (error: any, fallback: string) => {
        const detail = error?.response?.data?.error
        return (Array.isArray(detail) ? detail.join(' ') : detail)
            ?? error?.response?.data?.detail
            ?? fallback
    }

    const handleCreateLobby = async () => {
        setCreateError(null)
        try {
            const data = await createLobby()
            navigate('/lobby', { state: { sessionUuid: data.session_uuid } })
        } catch (error: any) {
            const status = error?.response?.status ?? 500
            const message = extractError(error, 'Failed to create a game. Please try again.')
            // 5xx is a genuine server failure → full error page; 4xx is shown inline.
            if (status >= 500) {
                navigate('/error', { state: { code: status, message } })
            } else {
                setCreateError(message)
            }
        }
    }

    const handleJoinLobby = async () => {
        const uuid = joinUuid.trim()
        if (!uuid) return
        if (uuid.length !== UUID_LENGTH) {
            setJoinError('Invalid lobby UUID.')
            return
        }
        setJoinError(null)
        try {
            await joinLobby(uuid)
            setShowJoinModal(false)
            navigate('/lobby', { state: { sessionUuid: uuid } })
        } catch (error: any) {
            const status = error?.response?.status ?? 500
            const message = extractError(error, 'Failed to join lobby. Check the UUID and try again.')
            // 5xx is a genuine server failure → full error page; 4xx is shown inline.
            if (status >= 500) {
                navigate('/error', { state: { code: status, message } })
            } else {
                setJoinError(message)
            }
        }
    }

    return {
        user,
        setUser: setUserCtx,
        handleLogout,
        handleCreateLobby,
        handleJoinLobby,
        joinUuid, setJoinUuid,
        joinError, setJoinError,
        createError, setCreateError,
        showJoinModal, setShowJoinModal: openJoinModal,
        showRulesModal, setShowRulesModal,
    }
}
