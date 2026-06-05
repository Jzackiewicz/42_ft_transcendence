import axios from 'axios';

const BASE = 'api/';

export const apiClient = axios.create({
	baseURL: BASE,
	withCredentials: true,
});

// Getting a CSRF token from cookies
apiClient.interceptors.request.use((config) => {
	const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
	const csrfToken = cookie ? cookie.split('=')[1] : '';

	if (csrfToken) {
		config.headers['X-CSRFToken'] = csrfToken;
	}
	return config;
});
