import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";

// Mock the auth boundary globally: components render as an authenticated "test-user"
// without touching Supabase or the network. Individual tests can override these mocks.
vi.mock("@/lib/auth/AuthService", () => {
  const user = { id: "test-user", email: "test@example.com", isDemo: false };
  const session = { accessToken: "test-token", user };
  return {
    authService: {
      getSession: vi.fn().mockResolvedValue(session),
      getAccessToken: vi.fn().mockResolvedValue("test-token"),
      onAuthStateChange: vi.fn(() => () => {}),
      hasDemo: vi.fn(() => true),
      signInWithPassword: vi.fn().mockResolvedValue(session),
      signUp: vi.fn().mockResolvedValue({ needsEmailConfirmation: false }),
      signInWithDemo: vi.fn().mockResolvedValue(session),
      signInWithOAuth: vi.fn().mockResolvedValue(undefined),
      resetPassword: vi.fn().mockResolvedValue(undefined),
      signOut: vi.fn().mockResolvedValue(undefined),
    },
  };
});

// jsdom lacks these; components (and React Flow) touch them.
if (!window.matchMedia) {
  window.matchMedia = vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));
}

class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
if (!("ResizeObserver" in globalThis)) {
  (globalThis as unknown as { ResizeObserver: unknown }).ResizeObserver =
    ResizeObserverStub;
}
