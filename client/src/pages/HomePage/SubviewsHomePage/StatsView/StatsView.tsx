import { useStatsView } from './useStatsView'
import { Card } from '../../../../components/Card/Card'
import { SectionTitle } from '../../../../components/SectionTitle/SectionTitle'
import { cx } from '../../../../utils/cx'
import styles from './StatsView.module.css'

function StatsView() {
    const stats = useStatsView()

    return (
        <Card>
            <SectionTitle>📊 Statistics</SectionTitle>

            <div className={styles['stats-grid']}>
                <div className={styles['stat-box']}>
                    <div className={cx(styles['stat-box-val'], styles['stat-box-val--cyan'])}>{stats.gamesPlayed}</div>
                    <div className={styles['stat-box-lbl']}>Games Played</div>
                </div>
                <div className={styles['stat-box']}>
                    <div className={cx(styles['stat-box-val'], styles['stat-box-val--magenta'])}>{stats.wins}</div>
                    <div className={styles['stat-box-lbl']}>Wins</div>
                </div>
                <div className={styles['stat-box']}>
                    <div className={cx(styles['stat-box-val'], styles['stat-box-val--gold'])}>{stats.winRate}%</div>
                    <div className={styles['stat-box-lbl']}>Win Rate</div>
                </div>
                <div className={styles['stat-box']}>
                    <div className={cx(styles['stat-box-val'], styles['stat-box-val--green'])}>{stats.avgScore}</div>
                    <div className={styles['stat-box-lbl']}>Avg Score</div>
                </div>
                <div className={styles['stat-box']}>
                    <div className={cx(styles['stat-box-val'], styles['stat-box-val--red'])}>{stats.correctRate}%</div>
                    <div className={styles['stat-box-lbl']}>Correct Rate</div>
                </div>
                <div className={styles['stat-box']}>
                    <div className={cx(styles['stat-box-val'], styles['stat-box-val--violet'])}>{stats.bestStreak}</div>
                    <div className={styles['stat-box-lbl']}>Best Streak</div>
                </div>
            </div>
        </Card>
    )
}

export default StatsView
