import { cx } from '../../utils/cx';
import styles from './Icon.module.css';

type Size = 'xs' | 'sm' | 'md' | 'lg';

const sizeMap: Record<Size, number> = {
    xs: 14,
    sm: 16,
    md: 21,
    lg: 28,
};

/* Custom icon set for the design system. */
const stroke = {
    stroke: 'currentColor',
    strokeWidth: 1.5,
    strokeLinecap: 'round',
    strokeLinejoin: 'round',
    fill: 'none',
} as const;

const icons = {
    check: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <path d="M3 8.5L6.5 12L13 4.5" {...stroke} />
        </svg>
    ),
    close: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <path d="M4 4l8 8M12 4l-8 8" {...stroke} />
        </svg>
    ),
    edit: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <path d="M11.3 2.2a1.9 1.9 0 0 1 2.5 2.5L5 13.7 1.5 14.5 2.3 11z" {...stroke} />
            <path d="M10.5 3l2.5 2.5" {...stroke} />
        </svg>
    ),
    copy: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <rect x="5" y="5" width="9" height="9" rx="1.5" {...stroke} />
            <path d="M3 11V3.5C3 2.67 3.67 2 4.5 2H11" {...stroke} />
        </svg>
    ),
    clock: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <circle cx="8" cy="8" r="6" {...stroke} />
            <path d="M8 4.5V8l2.5 1.5" {...stroke} />
        </svg>
    ),
    heart: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <path
                d="M8 13.5S2.5 9.8 2.5 6.3A2.8 2.8 0 0 1 8 5 2.8 2.8 0 0 1 13.5 6.3C13.5 9.8 8 13.5 8 13.5z"
                fill="currentColor"
            />
        </svg>
    ),
    heartOutline: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <path
                d="M8 13.5S2.5 9.8 2.5 6.3A2.8 2.8 0 0 1 8 5 2.8 2.8 0 0 1 13.5 6.3C13.5 9.8 8 13.5 8 13.5z"
                {...stroke}
            />
        </svg>
    ),
    trophy: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <path d="M4.5 2.5h7V6a3.5 3.5 0 0 1-7 0V2.5z" {...stroke} />
            <path d="M4.5 3.5H3A1.5 1.5 0 0 0 3 6.5h1.5M11.5 3.5H13a1.5 1.5 0 0 1 0 3h-1.5" {...stroke} />
            <path d="M8 9.5v2M6 13.5h4M6.5 11.5h3" {...stroke} />
        </svg>
    ),
    chart: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <rect x="2" y="8" width="3" height="6" rx="0.5" {...stroke} />
            <rect x="6.5" y="5" width="3" height="9" rx="0.5" {...stroke} />
            <rect x="11" y="2" width="3" height="12" rx="0.5" {...stroke} />
        </svg>
    ),
    eye: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <path d="M1.5 8S4 3.5 8 3.5 14.5 8 14.5 8 12 12.5 8 12.5 1.5 8 1.5 8z" {...stroke} />
            <circle cx="8" cy="8" r="2" {...stroke} />
        </svg>
    ),
    skull: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <path d="M3 7.5a5 5 0 0 1 10 0V10a1.5 1.5 0 0 1-1.5 1.5H11V13H5v-1.5H4.5A1.5 1.5 0 0 1 3 10V7.5z" {...stroke} />
            <circle cx="6" cy="8" r="1.2" fill="currentColor" />
            <circle cx="10" cy="8" r="1.2" fill="currentColor" />
        </svg>
    ),
    users: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <circle cx="6" cy="5.5" r="2.5" {...stroke} />
            <path d="M1.5 13c0-2.5 2-4 4.5-4s4.5 1.5 4.5 4" {...stroke} />
            <path d="M11 3.2a2.5 2.5 0 0 1 0 4.6M11.5 9.2c1.8.3 3 1.7 3 3.8" {...stroke} />
        </svg>
    ),
    signalOff: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <path d="M2 6.3a9 9 0 0 1 12 0M4 8.8a5.5 5.5 0 0 1 8 0M6 11.3a2 2 0 0 1 4 0" {...stroke} />
            <path d="M2.5 13.5L13.5 2.5" {...stroke} />
        </svg>
    ),
    arrowLeft: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <path d="M7 3.5L2.5 8 7 12.5M2.5 8H13" {...stroke} />
        </svg>
    ),
    arrowRight: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <path d="M9 3.5L13.5 8 9 12.5M13.5 8H3" {...stroke} />
        </svg>
    ),
    play: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <path d="M5 3.5v9l7.5-4.5z" fill="currentColor" />
        </svg>
    ),
    enter: (s: number) => (
        <svg width={s} height={s} viewBox="0 0 16 16">
            <path d="M8.5 2.5h4a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1h-4" {...stroke} />
            <path d="M2.5 8h7M7 5.5L9.5 8 7 10.5" {...stroke} />
        </svg>
    ),
} as const;

export type IconName = keyof typeof icons;

interface IconProps {
    name: IconName;
    size?: Size;
    className?: string;
}

export function Icon({ name, size = 'sm', className }: IconProps) {
    return (
        <span className={cx(styles.icon, className)} aria-hidden="true">
            {icons[name](sizeMap[size])}
        </span>
    );
}

export default Icon;
