import React from 'react';
import { cx } from '../../utils/cx';
import styles from './Card.module.css';

interface CardProps {
    children: React.ReactNode;
    className?: string;
}

export function Card({ children, className }: CardProps) {
    return <div className={cx(styles.card, className)}>{children}</div>;
}

export default Card;
