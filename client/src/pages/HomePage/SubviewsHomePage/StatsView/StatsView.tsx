import { useStatsView } from './useStatsView'
import { Card } from '../../../../components/Card/Card'
import { SectionTitle } from '../../../../components/SectionTitle/SectionTitle'
import { Icon } from '../../../../components/Icon/Icon'
import { useUser } from '../../../../context/UserContext'
import { cx } from '../../../../utils/cx'
import styles from './StatsView.module.css'

function StatsView() {
    const { user } = useUser()
    const stats = useStatsView(user?.id)

    return (
        <Card>
            <SectionTitle><Icon name="chart" size="md" /> Statistics</SectionTitle>

            <div className={styles.statsGrid}>
                <div className={styles.statBox}>
                    <div className={cx(styles.statBoxVal, styles.statBoxValCyan)}>{stats.games_played}</div>
                    <div className={styles.statBoxLbl}>Games Played</div>
                </div>
                <div className={styles.statBox}>
                    <div className={cx(styles.statBoxVal, styles.statBoxValMagenta)}>{stats.wins}</div>
                    <div className={styles.statBoxLbl}>Wins</div>
                </div>
                <div className={styles.statBox}>
                    <div className={cx(styles.statBoxVal, styles.statBoxValGold)}>{stats.win_rate}%</div>
                    <div className={styles.statBoxLbl}>Win Rate</div>
                </div>
                <div className={styles.statBox}>
                    <div className={cx(styles.statBoxVal, styles.statBoxValGreen)}>{stats.avg_score}</div>
                    <div className={styles.statBoxLbl}>Avg Score</div>
                </div>
                <div className={styles.statBox}>
                    <div className={cx(styles.statBoxVal, styles.statBoxValRed)}>{stats.correct_rate}%</div>
                    <div className={styles.statBoxLbl}>Correct Rate</div>
                </div>
                <div className={styles.statBox}>
                    <div className={cx(styles.statBoxVal, styles.statBoxValViolet)}>{stats.highest_score}</div>
                    <div className={styles.statBoxLbl}>Best Score</div>
                </div>
            </div>
        </Card>
    )
}

export default StatsView
