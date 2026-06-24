import React from 'react';
import { cx } from '../../utils/cx';
import styles from './StatsGrid.module.css';

export type StatColor = 'cyan' | 'magenta' | 'gold' | 'green' | 'red' | 'violet';

const colorClass: Record<StatColor, string> = {
    cyan: styles.statBoxValCyan,
    magenta: styles.statBoxValMagenta,
    gold: styles.statBoxValGold,
    green: styles.statBoxValGreen,
    red: styles.statBoxValRed,
    violet: styles.statBoxValViolet,
};

export function StatsGrid({ children, className }: { children: React.ReactNode; className?: string }) {
    return <div className={cx(styles.statsGrid, className)}>{children}</div>;
}

interface StatTileProps {
    value: React.ReactNode;
    label: string;
    color?: StatColor;
}

export function StatTile({ value, label, color = 'cyan' }: StatTileProps) {
    return (
        <div className={styles.statBox}>
            <div className={cx(styles.statBoxVal, colorClass[color])}>{value}</div>
            <div className={styles.statBoxLbl}>{label}</div>
        </div>
    );
}

export default StatsGrid;
