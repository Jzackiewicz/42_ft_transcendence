import React from 'react';
import { cx } from '../../utils/cx';
import styles from './Button.module.css';

type Variant = 'primary' | 'secondary' | 'danger' | 'success';
type Size = 'sm' | 'md' | 'lg';

const variantClass: Record<Variant, string> = {
    primary: styles.appBtnPrimary,
    secondary: styles.appBtnSecondary,
    danger: styles.appBtnDanger,
    success: styles.appBtnSuccess,
};

const sizeClass: Record<Size, string> = {
    sm: styles.appBtnSm,
    md: styles.appBtnMd,
    lg: styles.appBtnLg,
};

interface ButtonProps {
    variant?: Variant;
    size?: Size;
    disabled?: boolean;
    onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
    type?: 'button' | 'submit' | 'reset';
    children: React.ReactNode;
    className?: string;
}

export function Button({
    variant = 'primary',
    size = 'md',
    disabled = false,
    onClick,
    type = 'button',
    children,
    className = ''
}: ButtonProps) {
    const classNames = cx(
        styles.appBtn,
        variantClass[variant],
        sizeClass[size],
        className
    );

    return (
        <button
            type={type}
            disabled={disabled}
            onClick={onClick}
            className={classNames}
        >
            {children}
        </button>
    );
}

export default Button;
