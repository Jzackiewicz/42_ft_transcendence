import { useStatsView } from './useStatsView'
import { Card } from '../../../../components/Card/Card'
import { SectionTitle } from '../../../../components/SectionTitle/SectionTitle'
import './StatsView.css'

function StatsView() {
    const stats = useStatsView()

    return (
        <Card>
            <SectionTitle>📊 Statistics</SectionTitle>

            <div className="stats-grid">
                <div className="stat-box">
                    <div className="stat-box-val stat-box-val--cyan">{stats.gamesPlayed}</div>
                    <div className="stat-box-lbl">Games Played</div>
                </div>
                <div className="stat-box">
                    <div className="stat-box-val stat-box-val--magenta">{stats.wins}</div>
                    <div className="stat-box-lbl">Wins</div>
                </div>
                <div className="stat-box">
                    <div className="stat-box-val stat-box-val--gold">{stats.winRate}%</div>
                    <div className="stat-box-lbl">Win Rate</div>
                </div>
                <div className="stat-box">
                    <div className="stat-box-val stat-box-val--green">{stats.avgScore}</div>
                    <div className="stat-box-lbl">Avg Score</div>
                </div>
                <div className="stat-box">
                    <div className="stat-box-val stat-box-val--red">{stats.correctRate}%</div>
                    <div className="stat-box-lbl">Correct Rate</div>
                </div>
                <div className="stat-box">
                    <div className="stat-box-val stat-box-val--violet">{stats.bestStreak}</div>
                    <div className="stat-box-lbl">Best Streak</div>
                </div>
            </div>
        </Card>
    )
}

export default StatsView
