import { Link } from 'react-router-dom';
import { useErrorPage } from './useErrorPage';
import styles from './ErrorPage.module.css';

export function ErrorPage() {
    const { code, message } = useErrorPage();

    return (
        <div className={styles['error-page']}>
            <h1 className={styles['error-code']}>{code}</h1>
            <h2 className={styles['error-title']}>Something went wrong</h2>
            <p className={styles['error-msg']}>{message}</p>
            <Link to="/" className={styles['home-btn']}>
                Return to Safety
            </Link>
        </div>
    );
}
