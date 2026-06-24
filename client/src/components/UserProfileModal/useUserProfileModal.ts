import { useEffect, useState } from 'react'
import { getUserStats } from '../../api/gameWrapper'

interface UserStats {
    games_played: number
    wins: number
    win_rate: number
    avg_score: number
    highest_score: number
    correct_rate: number
}

export function useUserProfileModal(userId: number) {
    const [stats, setStats] = useState<UserStats | null>(null)

    useEffect(() => {
        setStats(null)
        getUserStats(userId).then(setStats).catch(() => {})
    }, [userId])

    return { stats }
}
