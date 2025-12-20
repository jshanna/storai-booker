import { test, expect } from '@playwright/test';

test.describe('Browse Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/browse');
  });

  test('displays page heading', async ({ page }) => {
    await expect(page.getByRole('heading').first()).toBeVisible();
  });

  test('displays content area', async ({ page }) => {
    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Page should have main content area
    await expect(page.locator('main, [role="main"], .container').first()).toBeVisible();
  });

  test('has filter controls', async ({ page }) => {
    // Should have some filter controls (dropdowns)
    const controls = page.locator('button, [role="combobox"]');
    await expect(controls.first()).toBeVisible();
  });
});
