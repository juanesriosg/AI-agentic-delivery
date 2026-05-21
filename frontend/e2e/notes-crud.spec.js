import { test, expect } from "@playwright/test";

test.describe("Notes CRUD smoke", () => {
  test("creates, edits, and deletes a note", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("heading", { name: "Notes CRUD" })).toBeVisible();

    await page.getByLabel("Title").fill("Playwright note");
    await page.getByLabel("Body").fill("Body from E2E");
    await page.getByRole("button", { name: "Save" }).click();

    await expect(page.getByText("Note created.")).toBeVisible();
    await expect(page.getByText("Playwright note")).toBeVisible();

    await page.getByRole("button", { name: "Edit" }).click();
    await page.getByLabel("Title").fill("Updated note");
    await page.getByRole("button", { name: "Save" }).click();

    await expect(page.getByText("Note updated.")).toBeVisible();

    await page.getByRole("button", { name: "Delete" }).click();
    await expect(page.getByText("Note deleted.")).toBeVisible();
  });
});
