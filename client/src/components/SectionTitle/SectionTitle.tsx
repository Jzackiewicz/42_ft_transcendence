import React from 'react';
import { cx } from '../../utils/cx';
import styles from './SectionTitle.module.css';

interface SectionTitleProps {
    /** Element to render as (e.g. 'h3' for semantic headings). Defaults to 'div'. */
    as?: React.ElementType;
    children: React.ReactNode;
    className?: string;
}

export function SectionTitle({ as: Tag = 'div', children, className }: SectionTitleProps) {
    return <Tag className={cx(styles.sectionTitle, className)}>{children}</Tag>;
}

export default SectionTitle;
