import { test, expect } from '@playwright/test';

test.describe('Authentication Page', () => {
	test.beforeEach(async ({ page }) => {
		// Routes used in main.tsx is /login
		await page.goto('/login');
	});

	test('should display login form by default', async ({ page }) => {
		// Wait for content to appear (UserContext might take a moment to fetch /me)
		await expect(page.locator('.auth-title')).toBeVisible({ timeout: 10000 });
		await expect(page.locator('.auth-title')).toHaveText('Welcome back');
		await expect(page.getByPlaceholder('Enter your username')).toBeVisible();
		await expect(page.getByPlaceholder('Enter your password')).toBeVisible();
	});

	test('should toggle between login and registration', async ({ page }) => {
		await page.getByRole('button', { name: 'Register' }).click();
		await expect(page.locator('.auth-title')).toHaveText('Join the Show');

		await page.getByRole('button', { name: 'Sign In' }).click();
		await expect(page.locator('.auth-title')).toHaveText('Welcome back');
	});

	test('should show error on empty login', async ({ page }) => {
		// Wait for form
		await page.waitForSelector('.auth-submit');
		await page.getByRole('button', { name: 'Sign In ⟶' }).click();

		// In InputField.tsx, error class is .inputfield-warning
		const errors = page.locator('.inputfield-warning, .form-error');
		await expect(errors.first()).toBeVisible();
	});
});
