import { test, expect } from '@playwright/test';

test.describe('Authentication Page', () => {
	test.beforeEach(async ({ page }) => {
		// Routes used in main.tsx is /login
		await page.goto('/login');
	});

	test('should display login form by default', async ({ page }) => {
		// Wait for content to appear (UserContext might take a moment to fetch /me)
		await expect(page.getByText('Welcome back', { exact: true })).toBeVisible({ timeout: 10000 });
		await expect(page.getByPlaceholder('Enter your email or username')).toBeVisible();
		await expect(page.getByPlaceholder('Enter your password')).toBeVisible();
	});

	test('should toggle between login and registration', async ({ page }) => {
		await page.getByRole('button', { name: 'Register', exact: true }).click();
		await expect(page.getByText('Join the Show', { exact: true })).toBeVisible();

		await page.getByRole('button', { name: 'Sign In', exact: true }).click();
		await expect(page.getByText('Welcome back', { exact: true })).toBeVisible();
	});

	test('should show error on empty login', async ({ page }) => {
		await page.getByRole('button', { name: 'Sign In ⟶' }).click();

		// preValidateLoginParams in useLoginView.ts surfaces this on an empty form
		await expect(page.getByText('Email or username is required')).toBeVisible();
	});
});
