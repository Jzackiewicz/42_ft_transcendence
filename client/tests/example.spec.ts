import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
	await page.goto('/');
	// Basic check for app load
	await expect(page).toHaveTitle(/Quizscendence/i);
});
