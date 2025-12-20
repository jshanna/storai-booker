import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('displays hero section', async ({ page }) => {
    // Check for main heading
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();

    // Check for CTA button
    await expect(page.getByRole('link', { name: /create/i })).toBeVisible();
  });

  test('displays feature cards', async ({ page }) => {
    // Check for feature descriptions
    await expect(page.getByText(/personalized stories/i)).toBeVisible();
    await expect(page.getByText(/illustrations/i)).toBeVisible();
    await expect(page.getByText(/formats/i)).toBeVisible();
  });

  test('CTA button links to generate page or login', async ({ page }) => {
    const ctaButton = page.getByRole('link', { name: /create/i });
    await ctaButton.click();

    // Either goes to generate page or redirects to login (if auth required)
    await expect(page).toHaveURL(/generate|login/);
  });

  test('has responsive navigation', async ({ page }) => {
    // Desktop navigation should be visible
    await expect(page.getByRole('navigation')).toBeVisible();
  });
});

test.describe('Navigation', () => {
  test('header contains logo/brand', async ({ page }) => {
    await page.goto('/');

    const header = page.locator('header');
    await expect(header).toBeVisible();
  });

  test('can navigate to browse page', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('link', { name: /browse/i }).click();

    await expect(page).toHaveURL('/browse');
  });

  test('can navigate to generate page or login', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('link', { name: /generate/i }).click();

    // Either goes to generate page or redirects to login (if auth required)
    await expect(page).toHaveURL(/generate|login/);
  });

  test('displays language selector', async ({ page }) => {
    await page.goto('/');

    // Find the language selector button (globe icon)
    const langSelector = page.locator('button').filter({ has: page.locator('svg') }).first();
    await expect(langSelector).toBeVisible();
  });
});

test.describe('Language Switching', () => {
  test('can switch to Spanish', async ({ page }) => {
    await page.goto('/');

    // Open language selector
    await page.locator('header button').filter({ has: page.locator('svg') }).first().click();

    // Click Spanish option
    await page.getByRole('menuitem', { name: /español/i }).click();

    // Check that some text changed to Spanish (e.g., navigation items)
    await expect(page.getByText(/explorar|generar|inicio/i).first()).toBeVisible();
  });

  test('can switch to French', async ({ page }) => {
    await page.goto('/');

    // Open language selector
    await page.locator('header button').filter({ has: page.locator('svg') }).first().click();

    // Click French option
    await page.getByRole('menuitem', { name: /français/i }).click();

    // Check that some text changed to French
    await expect(page.getByText(/parcourir|générer|accueil/i).first()).toBeVisible();
  });

  test('language preference persists across navigation', async ({ page }) => {
    await page.goto('/');

    // Switch to Spanish
    await page.locator('header button').filter({ has: page.locator('svg') }).first().click();
    await page.getByRole('menuitem', { name: /español/i }).click();

    // Navigate to another page
    await page.goto('/browse');

    // Spanish text should still be present
    await expect(page.getByText(/explorar|buscar/i).first()).toBeVisible();
  });
});
