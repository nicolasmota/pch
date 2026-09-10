import { expect, test } from "@playwright/test";

test("guided setup shows key storage sentence", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByText(/Key stored in your system keychain|Key stored in a private file in ~\/\.pch/),
  ).toBeVisible();
});
