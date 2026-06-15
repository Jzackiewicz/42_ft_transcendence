import { useLocation } from 'react-router-dom';
import { useEffect } from 'react';

interface ErrorState {
    code?: string | number;
    message?: string;
}

export function useErrorPage() {
    const location = useLocation();
    const state = location.state as ErrorState;

    // Check state first (SPA navigation), then sessionStorage (hard redirect)
    const code = state?.code || sessionStorage.getItem('lastErrorStatus') || '404';
    let message = state?.message;

    useEffect(() => {
        // Clear storage after render so it doesn't leak to future 404s
        sessionStorage.removeItem('lastErrorStatus');
    }, []);

    const isServerError = code.toString().startsWith('5');

    if (!message) {
        if (isServerError) {
            message = "Internal Server Error. It's our fault, not yours. We're looking into it.";
        } else {
            message = "The page you're looking for doesn't exist or an unexpected error occurred.";
        }
    }

    return { code, message };
}
