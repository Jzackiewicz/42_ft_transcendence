import React from 'react';
import { cx } from '../../utils/cx';
import styles from './Button.module.css';

type Variant = 'primary' | 'secondary' | 'danger' | 'dangerGhost' | 'success' | 'gradient' | 'ghost';
type Size = 'sm' | 'md' | 'lg';

const variantClass: Record<Variant, string> = {
    primary: styles.appBtnPrimary,
    secondary: styles.appBtnSecondary,
    danger: styles.appBtnDanger,
    dangerGhost: styles.appBtnDangerGhost,
    success: styles.appBtnSuccess,
    gradient: styles.appBtnGradient,
    ghost: styles.appBtnGhost,
};

const sizeClass: Record<Size, string> = {
    sm: styles.appBtnSm,
    md: styles.appBtnMd,
    lg: styles.appBtnLg,
};

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: Variant;
    size?: Size;
    /** Stretch to fill the container width (e.g. form submit buttons). */
    fullWidth?: boolean;
}

export function Button({
    variant = 'primary',
    size = 'md',
    fullWidth = false,
    type = 'button',
    className = '',
    children,
    ...rest
}: ButtonProps) {
    const classNames = cx(
        styles.appBtn,
        variantClass[variant],
        sizeClass[size],
        fullWidth && styles.appBtnFull,
        className
    );

    return (
        <button type={type} className={classNames} {...rest}>
            {children}
        </button>
    );
}

export default Button;
