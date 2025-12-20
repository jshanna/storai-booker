import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.describe('Login Page', () => {
    test('displays login form', async ({ page }) => {
      await page.goto('/login');

      // Check form elements are present
      await expect(page.locator('input[type="email"], input[name="email"], #email')).toBeVisible();
      await expect(page.locator('input[type="password"], input[name="password"], #password')).toBeVisible();
      await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    });

    test('has link to registration page', async ({ page }) => {
      await page.goto('/login');

      const signUpLink = page.getByRole('link', { name: /sign up/i }).first();
      await expect(signUpLink).toBeVisible();
    });

    test('has link to forgot password', async ({ page }) => {
      await page.goto('/login');

      await expect(page.getByText(/forgot password/i)).toBeVisible();
    });
  });

  test.describe('Registration Page', () => {
    test('displays registration form', async ({ page }) => {
      await page.goto('/register');

      await expect(page.locator('input[name="full_name"], #full_name')).toBeVisible();
      await expect(page.locator('input[type="email"], input[name="email"], #email')).toBeVisible();
      await expect(page.locator('input[type="password"]').first()).toBeVisible();
      await expect(page.getByRole('button', { name: /sign up/i })).toBeVisible();
    });

    test('has link to login page', async ({ page }) => {
      await page.goto('/register');

      const signInLink = page.getByRole('link', { name: /sign in/i });
      await expect(signInLink).toBeVisible();
    });

    test('shows password requirements when typing', async ({ page }) => {
      await page.goto('/register');

      // Start typing password to show requirements
      const passwordInput = page.locator('#password, input[name="password"]').first();
      await passwordInput.fill('a');

      // Password requirements should be visible
      await expect(page.getByText(/8 characters/i)).toBeVisible();
    });
  });

  test.describe('Protected Routes', () => {
    test('redirects to login when accessing library without auth', async ({ page }) => {
      await page.goto('/library');

      // Should redirect to login
      await expect(page).toHaveURL(/login/);
    });

    test('redirects to login when accessing settings without auth', async ({ page }) => {
      await page.goto('/settings');

      // Should redirect to login
      await expect(page).toHaveURL(/login/);
    });
  });
});
