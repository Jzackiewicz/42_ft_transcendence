import { useEffect, useState } from 'react'
import { getUserStats } from '../../../../api/gameWrapper'


export interface Stats {
    games_played: number
    wins: number
    win_rate: number
    avg_score: number
    correct_rate: number
    highest_score: number
}

const ZERO_STATS: Stats = {
    games_played: 0,
    wins: 0,
    win_rate: 0,
    avg_score: 0,
    correct_rate: 0,
    highest_score: 0,
}

export function useStatsView(userId: number | undefined): Stats {
    const [stats, setStats] = useState<Stats>(ZERO_STATS)

    useEffect(() => {
        if (userId === undefined) return
        getUserStats(userId).then(setStats)
    }, [userId])

    return stats
}
