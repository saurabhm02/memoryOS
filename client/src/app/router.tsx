import { Loader2 } from "lucide-react";
import { Suspense, lazy } from "react";
import { Outlet, createBrowserRouter } from "react-router-dom";

import { AppShell } from "@/components/AppShell";
import { ProtectedRoute, PublicOnlyRoute } from "@/components/ProtectedRoute";

// Route-level code splitting: each screen loads in its own chunk.
const SessionScreen = lazy(() =>
  import("@/screens/SessionScreen").then((m) => ({ default: m.SessionScreen })),
);
const MemoryScreen = lazy(() =>
  import("@/screens/MemoryScreen").then((m) => ({ default: m.MemoryScreen })),
);
const LandingScreen = lazy(() =>
  import("@/screens/LandingScreen").then((m) => ({ default: m.LandingScreen })),
);
const LoginScreen = lazy(() =>
  import("@/screens/LoginScreen").then((m) => ({ default: m.LoginScreen })),
);
const RegisterScreen = lazy(() =>
  import("@/screens/RegisterScreen").then((m) => ({ default: m.RegisterScreen })),
);
const ForgotPasswordScreen = lazy(() =>
  import("@/screens/ForgotPasswordScreen").then((m) => ({
    default: m.ForgotPasswordScreen,
  })),
);
const AuthCallbackScreen = lazy(() =>
  import("@/screens/AuthCallbackScreen").then((m) => ({ default: m.AuthCallbackScreen })),
);

/** A single Suspense boundary for every route, so navigating to a lazily-loaded screen
 * shows a loader instead of suspending during the click (which React 18 treats as a
 * synchronous-input suspension and surfaces as a crash). */
function RootBoundary() {
  return (
    <Suspense
      fallback={
        <div className="grid min-h-dvh place-items-center bg-bg">
          <Loader2
            className="h-6 w-6 animate-spin text-ink-subtle"
            aria-label="Loading"
          />
        </div>
      }
    >
      <Outlet />
    </Suspense>
  );
}

export const router = createBrowserRouter([
  {
    element: <RootBoundary />,
    children: [
      {
        path: "/landing",
        element: (
          <PublicOnlyRoute>
            <LandingScreen />
          </PublicOnlyRoute>
        ),
      },
      {
        path: "/login",
        element: (
          <PublicOnlyRoute>
            <LoginScreen />
          </PublicOnlyRoute>
        ),
      },
      {
        path: "/register",
        element: (
          <PublicOnlyRoute>
            <RegisterScreen />
          </PublicOnlyRoute>
        ),
      },
      {
        path: "/forgot-password",
        element: (
          <PublicOnlyRoute>
            <ForgotPasswordScreen />
          </PublicOnlyRoute>
        ),
      },
      { path: "/auth/callback", element: <AuthCallbackScreen /> },
      {
        path: "/",
        element: (
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        ),
        children: [
          { index: true, element: <SessionScreen /> },
          { path: "memory", element: <MemoryScreen /> },
        ],
      },
    ],
  },
]);
