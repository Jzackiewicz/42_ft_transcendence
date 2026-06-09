import { Link } from 'react-router-dom';
import { useErrorPage } from './useErrorPage';
import './ErrorPage.css';

export function ErrorPage() {
    const { code, message } = useErrorPage();

    return (
        <div className="error-page">
            <h1 className="error-code">{code}</h1>
            <h2 className="error-title">Something went wrong</h2>
            <p className="error-msg">{message}</p>
            <Link to="/" className="home-btn">
                Return to Safety
            </Link>
        </div>
    );
}
