import { expect, test } from "@playwright/test";

const DEMO_EMAIL = process.env.VITE_DEMO_EMAIL ?? "demo@recallos.app";
const DEMO_PASSWORD = process.env.VITE_DEMO_PASSWORD ?? "RecallOS-Demo-2026!";

test("landing renders and protected routes redirect when unauthenticated", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/landing$/);
  await expect(page.getByRole("heading", { name: /remembers you/i })).toBeVisible();
});

test("'Get started' navigates to register without suspending", async ({ page }) => {
  await page.goto("/landing");
  await page
    .getByRole("link", { name: /get started/i })
    .first()
    .click();
  await expect(page).toHaveURL(/\/register$/);
  await expect(page.getByRole("heading", { name: /create your account/i })).toBeVisible();
});

test("registration surfaces the email-verification step", async ({ page }) => {
  await page.goto("/register");
  const email = `e2e+${Date.now()}@recallos.app`;
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password", { exact: true }).fill("Sup3rsecret!");
  await page.getByRole("button", { name: /^create account$/i }).click();
  await expect(page.getByRole("heading", { name: /check your inbox/i })).toBeVisible();
});

test("login persists across reload, then logout returns to landing", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill(DEMO_EMAIL);
  await page.getByLabel("Password", { exact: true }).fill(DEMO_PASSWORD);
  await page.getByRole("button", { name: /^log in$/i }).click();

  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: /^Session$/ })).toBeVisible();

  // Session persistence: a reload keeps the user authenticated (no bounce to landing).
  await page.reload();
  await expect(page.getByRole("heading", { name: /^Session$/ })).toBeVisible();

  await page.getByRole("button", { name: /sign out/i }).click();
  await expect(page).toHaveURL(/\/landing$/);
});

test("'Try the demo' signs into the sandboxed demo account", async ({ page }) => {
  await page.goto("/landing");
  await page.getByRole("button", { name: /try the demo/i }).click();
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: /^Session$/ })).toBeVisible();
  await expect(page.getByText("Demo", { exact: true })).toBeVisible();
});
