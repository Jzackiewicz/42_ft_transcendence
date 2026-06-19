import React from 'react';
import './Button.css';

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
    const classNames = [
        'app-btn',
        `app-btn-${variant}`,
        `app-btn-${size}`,
        className
    ].filter(Boolean).join(' ');

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
