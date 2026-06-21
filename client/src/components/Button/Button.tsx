import React from 'react';
import { cx } from '../../utils/cx';
import styles from './Button.module.css';

interface ButtonProps {
    variant?: 'primary' | 'secondary' | 'danger' | 'success';
    size?: 'sm' | 'md' | 'lg';
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
    const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
    const classNames = cx(
        styles.appBtn,
        styles[`appBtn${cap(variant)}`],
        styles[`appBtn${cap(size)}`],
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
