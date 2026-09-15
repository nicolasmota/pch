import { expect, test } from "@playwright/test";

test("guided setup shows key storage sentence", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByText(/Key stored in your system keychain|Key stored in a private file in ~\/\.pch/),
  ).toBeVisible();
});

test("marketplace and simulator are off the default nav", async ({ page }) => {
  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "Main" });
  await expect(nav.getByRole("link", { name: "Home" })).toBeVisible();
  await expect(nav.getByRole("link", { name: "Marketplace" })).toHaveCount(0);
  await expect(nav.getByRole("link", { name: "Simulator" })).toHaveCount(0);
});
