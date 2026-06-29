/// <reference types="vitest/config" />
import path from "node:path";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
  server: { port: 5173 },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
    css: false,
    // Unit/component tests only; Playwright specs under e2e/ run via `playwright test`.
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
    // Supabase env so importing the client never throws in tests (the service is mocked).
    env: {
      VITE_SUPABASE_URL: "http://localhost:54321",
      VITE_SUPABASE_ANON_KEY: "test-anon-key",
      VITE_DEMO_EMAIL: "demo@recallos.app",
      VITE_DEMO_PASSWORD: "demo-password",
    },
  },
});
