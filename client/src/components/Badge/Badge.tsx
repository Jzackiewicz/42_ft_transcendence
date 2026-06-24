import React from 'react';
import { cx } from '../../utils/cx';
import styles from './Badge.module.css';

export type BadgeVariant = 'host' | 'answering' | 'nominator' | 'joined' | 'ai' | 'verified';

interface BadgeProps {
    variant: BadgeVariant;
    children: React.ReactNode;
    title?: string;
    className?: string;
}

export function Badge({ variant, children, title, className }: BadgeProps) {
    return (
        <span className={cx(styles.badge, styles[variant], className)} title={title}>
            {children}
        </span>
    );
}

export default Badge;
