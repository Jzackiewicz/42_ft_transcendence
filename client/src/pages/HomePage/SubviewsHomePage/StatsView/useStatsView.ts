// Stats will be fetched from the API in a future task.
// For now the hook returns zeroed-out values so the view has a stable shape.

export interface Stats {
    gamesPlayed: number
    wins:        number
    winRate:     number
    avgScore:    number
    correctRate: number
    bestStreak:  number
}

export function useStatsView(): Stats {
    return {
        gamesPlayed: 0,
        wins:        0,
        winRate:     0,
        avgScore:    0,
        correctRate: 0,
        bestStreak:  0,
    }
}
