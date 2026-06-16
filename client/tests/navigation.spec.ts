import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
	test('should load home page and redirect if unauthenticated', async ({ page }) => {
		await page.goto('/');
		// Home redirects to /login if no user (via RootRedirect)
		await expect(page).toHaveURL(/\/login/);
	});

	test('should show error page for non-existent routes', async ({ page }) => {
		await page.goto('/this-route-does-not-exist');
		// main.tsx: <Route path="*" element={<Navigate to="/error" replace />} />
		await expect(page).toHaveURL(/\/error/);
		await expect(page.locator('h1')).toContainText(/404/i);
	});
});
