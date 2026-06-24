import { apiClient } from './apiClient';

export async function register(username: string, email: string, password: string) {
	const res = await apiClient.post('/account/users/register/', { username, email, password });
	return res.data;
}

export async function login(identifier: string, password: string) {
	const res = await apiClient.post('/account/users/login/', { identifier, password });
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

export async function patchMe(fields: { username?: string; email?: string }) {
	const res = await apiClient.patch('/account/profiles/me/', fields);
	return res.data;
}

export async function uploadAvatar(userId: number, file: File) {
	const formData = new FormData();
	formData.append('avatar', file);
	const res = await apiClient.post(`/account/profiles/${userId}/avatar/`, formData, {
		headers: { 'Content-Type': 'multipart/form-data' },
	});
	return res.data;
}

export function googleOAuthLogin() {
	window.location.href = '/api/account/oauth/google/login/';
}
