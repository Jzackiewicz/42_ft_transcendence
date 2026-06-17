import { apiClient } from './apiClient';

export async function register(username: string, email: string, password: string) {
	const res = await apiClient.post('/account/users/register/', { username, email, password });
	return res.data;
}

export async function login(username: string, password: string) {
	console.log("Sending login request:", { username, password });
	const res = await apiClient.post('/account/users/login/', { username, password });
	console.log("Login response:", res.data);
	return res.data;
}

export async function logout() {
	await apiClient.post('/account/users/logout/');
}

export async function getUser(userId: number) {
	const res = await apiClient.get(`/account/users/${userId}/`);
	return res.data;
}

export async function getMe() {
	try {
		const res = await apiClient.get('/account/profiles/me/');
		return res.data;
	} catch (error) {
		return null;
	}
}

export function googleOAuthLogin() {
	window.location.href = '/api/account/oauth/google/login/';
}
