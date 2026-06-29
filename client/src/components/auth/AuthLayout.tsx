import { Brain } from "lucide-react";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";

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

/** The two-panel auth chrome: a brand panel that sells the product moment, and a focused
 * form column. The brand panel collapses on mobile. */
export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="grid min-h-dvh bg-bg md:grid-cols-[0.9fr_1.1fr]">
      <aside
        className="relative hidden flex-col justify-between border-r border-border p-10 md:flex"
        style={{
          background:
            "radial-gradient(70% 60% at 30% 30%, color-mix(in oklch, var(--primary) 24%, transparent), transparent 70%), radial-gradient(50% 50% at 80% 90%, color-mix(in oklch, var(--root-cause) 16%, transparent), transparent 70%)",
        }}
      >
        <Link to="/landing" className="w-fit">
          <Wordmark />
        </Link>
        <div className="max-w-sm">
          <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-root-cause">
            The memory moment
          </p>
          <p className="mt-3 text-pretty text-xl font-medium leading-snug text-ink">
            “Caching, database round-trips, and distributed transactions all trace to{" "}
            <span className="text-root-cause">Consistency Models</span> — your graph found
            that.”
          </p>
          <p className="mt-4 text-[13px] text-ink-muted">
            A persistent competency graph that gets sharper every session.
          </p>
        </div>
        <p className="text-[12px] text-ink-subtle">Built on Cognee · Open source</p>
      </aside>

      <main className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-sm animate-rise-in">
          <Link to="/landing" className="mb-8 flex w-fit md:hidden">
            <Wordmark />
          </Link>
          {children}
        </div>
      </main>
    </div>
  );
}
