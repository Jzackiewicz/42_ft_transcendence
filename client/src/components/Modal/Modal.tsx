import { useEffect } from 'react';
import { cx } from '../../utils/cx';
import styles from './Modal.module.css';

interface ModalProps {
    open: boolean;
    onClose: () => void;
    title?: React.ReactNode;
    children: React.ReactNode;
    className?: string;
}

export function Modal({ open, onClose, title, children, className }: ModalProps) {
    useEffect(() => {
        if (!open) return;
        const handler = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        document.addEventListener('keydown', handler);
        return () => document.removeEventListener('keydown', handler);
    }, [open, onClose]);

    if (!open) return null;

    return (
        <div
            className={styles.modalOverlay}
            onClick={onClose}
            role="dialog"
            aria-modal="true"
        >
            <div className={cx(styles.modalPanel, className)} onClick={e => e.stopPropagation()}>
                <button
                    className={styles.modalClose}
                    onClick={onClose}
                    aria-label="Close"
                >
                    &times;
                </button>
                {title && <h3 className={styles.modalTitle}>{title}</h3>}
                {children}
            </div>
        </div>
    );
}

export default Modal;
