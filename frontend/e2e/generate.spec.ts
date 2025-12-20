import { test, expect } from '@playwright/test';

test.describe('Story Generation Page', () => {
  test('redirects to login when not authenticated', async ({ page }) => {
    await page.goto('/generate');

    // Should redirect to login when not authenticated
    await expect(page).toHaveURL(/login/);
  });

  test('login page has email and password fields', async ({ page }) => {
    await page.goto('/generate');

    // Should be on login page
    await expect(page.locator('input[type="email"], #email')).toBeVisible();
    await expect(page.locator('input[type="password"], #password')).toBeVisible();
  });
});
