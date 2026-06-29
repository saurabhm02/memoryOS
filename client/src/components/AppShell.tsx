import { Brain, History, LogOut, type LucideIcon, Network } from "lucide-react";
import { Suspense } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/lib/auth/AuthProvider";
import { cn } from "@/lib/utils";

interface NavEntry {
  to: string;
  label: string;
  Icon: LucideIcon;
  end: boolean;
}

const NAV: NavEntry[] = [
  { to: "/", label: "Session", Icon: Network, end: true },
  { to: "/memory", label: "Memory", Icon: History, end: false },
];

function Wordmark() {
  return (
    <div className="flex items-center gap-2">
      <span className="grid h-7 w-7 place-items-center rounded-md bg-primary text-primary-ink">
        <Brain className="h-4 w-4" aria-hidden />
      </span>
      <span className="font-semibold tracking-tight text-ink">RecallOS</span>
    </div>
  );
}

function NavItem({ to, label, Icon, end }: NavEntry) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        cn(
          "flex items-center gap-2.5 rounded-md px-3 py-2 text-sm transition-colors",
          isActive
            ? "bg-surface-2 text-ink"
            : "text-ink-muted hover:bg-surface-2 hover:text-ink",
        )
      }
    >
      <Icon className="h-4 w-4" aria-hidden />
      {label}
    </NavLink>
  );
}

function UserCard() {
  const { user, signOut } = useAuth();
  const email = user?.email ?? "Signed in";
  return (
    <div className="rounded-md border border-border bg-surface-2 px-3 py-2.5">
      <div className="flex items-center justify-between gap-2">
        <p className="text-[11px] uppercase tracking-wide text-ink-subtle">Learner</p>
        {user?.isDemo && (
          <span className="rounded-full border border-root-cause bg-root-cause-bg px-1.5 py-0.5 text-[10px] font-medium text-root-cause">
            Demo
          </span>
        )}
      </div>
      <p className="mt-0.5 truncate text-[12px] text-ink-muted" title={email}>
        {email}
      </p>
      <p className="mt-1 text-[11px] text-ink-subtle">Backend Engineering</p>
      <button
        type="button"
        onClick={() => void signOut()}
        className="mt-2.5 inline-flex w-full items-center justify-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5 text-[12px] text-ink-muted transition-colors hover:border-border-strong hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
      >
        <LogOut className="h-3.5 w-3.5" aria-hidden /> Sign out
      </button>
    </div>
  );
}

export function AppShell() {
  const { signOut } = useAuth();

  return (
    <div className="flex h-dvh flex-col md:flex-row">
      {/* Mobile top bar */}
      <header className="flex items-center justify-between border-b border-border bg-surface px-4 py-3 md:hidden">
        <Wordmark />
        <div className="flex items-center gap-1">
          <nav className="flex gap-1" aria-label="Primary">
            {NAV.map((entry) => (
              <NavItem key={entry.to} {...entry} />
            ))}
          </nav>
          <button
            type="button"
            onClick={() => void signOut()}
            aria-label="Sign out"
            className="rounded-md p-2 text-ink-muted hover:bg-surface-2 hover:text-ink"
          >
            <LogOut className="h-4 w-4" aria-hidden />
          </button>
        </div>
      </header>

      {/* Desktop rail */}
      <aside className="hidden w-60 shrink-0 flex-col border-r border-border bg-surface px-3 py-4 md:flex">
        <div className="px-2">
          <Wordmark />
        </div>
        <nav className="mt-6 flex flex-col gap-1" aria-label="Primary">
          {NAV.map((entry) => (
            <NavItem key={entry.to} {...entry} />
          ))}
        </nav>
        <div className="mt-auto">
          <UserCard />
        </div>
      </aside>

      <main className="min-h-0 flex-1 overflow-hidden">
        <Suspense
          fallback={
            <div className="grid h-full place-items-center p-6">
              <Skeleton className="h-24 w-64" />
            </div>
          }
        >
          <Outlet />
        </Suspense>
      </main>
    </div>
  );
}
