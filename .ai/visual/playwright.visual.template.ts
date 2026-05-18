// Playwright visual QA scaffold. Copy into the repo's test structure and customize routes/selectors.
import { test, expect } from '@playwright/test';

const storyId = process.env.AGENT_STORY_ID || 'story-id';
const screenshotDir = `.agent/stories/${storyId}/screenshots`;

test.describe('visual QA states', () => {
  test('register form visual states', async ({ page }) => {
    await page.goto(process.env.AGENT_VISUAL_URL || '/register');
    await page.screenshot({ path: `${screenshotDir}/register-empty-desktop.png`, fullPage: true });

    // Customize selectors for the target repo.
    await page.getByLabel(/email/i).fill('invalid-email');
    await page.getByRole('button', { name: /register|submit|create/i }).click();
    await page.screenshot({ path: `${screenshotDir}/register-invalid-desktop.png`, fullPage: true });

    // Add assertions that make visual screenshots meaningful.
    await expect(page.getByText(/invalid|required|error/i).first()).toBeVisible();
  });
});
