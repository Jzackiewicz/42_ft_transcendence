import { Link } from 'react-router-dom';
import { useErrorPage } from './useErrorPage';
import styles from './ErrorPage.module.css';

export function ErrorPage() {
    const { code, message } = useErrorPage();

    return (
        <div className={styles.errorPage}>
            <h1 className={styles.errorCode}>{code}</h1>
            <h2 className={styles.errorTitle}>Something went wrong</h2>
            <p className={styles.errorMsg}>{message}</p>
            <Link to="/" className={styles.homeBtn}>
                Return to Safety
            </Link>
        </div>
    );
}
