import { defineConfig, devices } from "@playwright/test";

/** E2E against the already-running dev servers (client :5173, server :8000) and the
 * real gocognee Supabase project. Start both servers first, then `npx playwright test`. */
export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: "http://localhost:5173",
    headless: true,
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
