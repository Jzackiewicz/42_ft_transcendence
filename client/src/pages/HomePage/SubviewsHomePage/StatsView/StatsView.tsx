import { useStatsView } from './useStatsView'
import { Card } from '../../../../components/Card/Card'
import { SectionTitle } from '../../../../components/SectionTitle/SectionTitle'
import { Icon } from '../../../../components/Icon/Icon'
import { StatsGrid, StatTile } from '../../../../components/StatsGrid/StatsGrid'
import { useUser } from '../../../../context/UserContext'

function StatsView() {
    const { user } = useUser()
    const stats = useStatsView(user?.id)

    return (
        <Card>
            <SectionTitle><Icon name="chart" size="md" /> Statistics</SectionTitle>

            <StatsGrid>
                <StatTile value={stats.games_played} label="Games Played" color="cyan" />
                <StatTile value={stats.wins} label="Wins" color="magenta" />
                <StatTile value={`${stats.win_rate}%`} label="Win Rate" color="gold" />
                <StatTile value={stats.avg_score} label="Avg Score" color="green" />
                <StatTile value={`${stats.correct_rate}%`} label="Correct Rate" color="red" />
                <StatTile value={stats.highest_score} label="Best Score" color="violet" />
            </StatsGrid>
        </Card>
    )
}

export default StatsView
