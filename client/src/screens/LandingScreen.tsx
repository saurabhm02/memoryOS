import { Brain, Loader2 } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth/AuthProvider";

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

function GraphMotif() {
  return (
    <div className="relative hidden h-[360px] lg:block" aria-hidden>
      <svg className="absolute inset-0" width="100%" height="360" fill="none">
        <path d="M250 70 L250 150" stroke="var(--border-strong)" strokeWidth="1.5" />
        <path
          d="M235 196 C 170 235, 140 255, 110 286"
          stroke="var(--root-cause)"
          strokeWidth="2"
          strokeDasharray="5 5"
        />
        <path
          d="M255 196 L255 286"
          stroke="var(--root-cause)"
          strokeWidth="2"
          strokeDasharray="5 5"
        />
        <path
          d="M275 196 C 330 235, 360 255, 392 286"
          stroke="var(--root-cause)"
          strokeWidth="2"
          strokeDasharray="5 5"
        />
      </svg>
      <Node className="left-[180px] top-[30px]" tone="unvisited">
        CAP Theorem
      </Node>
      <Node className="left-[178px] top-[154px] shadow-root-cause" tone="root">
        Consistency Models
      </Node>
      <Node className="left-[40px] top-[286px]" tone="weak">
        Caching
      </Node>
      <Node className="left-[200px] top-[286px]" tone="weak">
        DB Round Trips
      </Node>
      <Node className="left-[355px] top-[286px]" tone="weak">
        Distributed Txns
      </Node>
    </div>
  );
}

function Node({
  children,
  className,
  tone,
}: {
  children: React.ReactNode;
  className?: string;
  tone: "unvisited" | "weak" | "root";
}) {
  const dot =
    tone === "weak" ? "bg-weak" : tone === "root" ? "bg-unvisited" : "bg-unvisited";
  return (
    <div
      className={`absolute flex h-[38px] w-[150px] items-center gap-2 rounded-md border bg-surface/70 px-3 font-mono text-[12px] text-ink backdrop-blur ${
        tone === "root" ? "border-root-cause" : "border-border"
      } ${className ?? ""}`}
    >
      <span className={`h-2 w-2 flex-none rounded-full ${dot}`} />
      {children}
    </div>
  );
}

export function LandingScreen() {
  const { signInWithDemo, hasDemo } = useAuth();
  const navigate = useNavigate();
  const [demoPending, setDemoPending] = useState(false);

  const onDemo = async () => {
    setDemoPending(true);
    try {
      await signInWithDemo();
      navigate("/", { replace: true });
    } finally {
      setDemoPending(false);
    }
  };

  return (
    <div
      className="min-h-dvh bg-bg"
      style={{
        background:
          "radial-gradient(60% 50% at 70% 15%, color-mix(in oklch, var(--primary) 20%, transparent), transparent 70%), radial-gradient(40% 40% at 85% 80%, color-mix(in oklch, var(--root-cause) 12%, transparent), transparent 70%)",
      }}
    >
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Wordmark />
        <nav className="flex items-center gap-2 text-sm">
          <Button asChild variant="ghost" size="sm">
            <Link to="/login">Log in</Link>
          </Button>
          <Button asChild size="sm">
            <Link to="/register">Get started</Link>
          </Button>
        </nav>
      </header>

      <main className="mx-auto grid max-w-6xl items-center gap-10 px-6 pb-16 pt-10 lg:grid-cols-[1.05fr_0.95fr] lg:pt-20">
        <div className="animate-rise-in">
          <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-root-cause">
            Persistent AI memory
          </p>
          <h1 className="mt-4 text-balance text-4xl font-semibold leading-[1.05] tracking-tight text-ink sm:text-5xl">
            The interview platform that{" "}
            <span className="text-root-cause">remembers you.</span>
          </h1>
          <p className="mt-5 max-w-xl text-pretty text-[15px] leading-relaxed text-ink-muted">
            RecallOS builds a living competency graph from every practice session and
            tells you the one concept to fix first — not another flat list of weaknesses.
            Your memory compounds, session over session.
          </p>
          <div className="mt-7 flex flex-wrap items-center gap-3">
            <Button asChild size="lg">
              <Link to="/register">Get started — it's free</Link>
            </Button>
            {hasDemo && (
              <Button variant="subtle" size="lg" onClick={onDemo} disabled={demoPending}>
                {demoPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                ) : (
                  <span className="relative flex h-1.5 w-1.5" aria-hidden>
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-root-cause opacity-60" />
                    <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-root-cause" />
                  </span>
                )}
                Try the demo
              </Button>
            )}
          </div>
          <p className="mt-5 text-[12px] text-ink-subtle">
            No credit card · Built on <span className="text-ink-muted">Cognee</span> ·
            Open source
          </p>
        </div>

        <GraphMotif />
      </main>

      <section className="mx-auto max-w-6xl px-6 pb-20">
        <div className="grid gap-4 rounded-xl border border-border bg-surface/60 p-5 sm:grid-cols-3">
          <div>
            <p className="font-mono text-[12px] text-root-cause">Remember</p>
            <p className="mt-1 text-[13px] text-ink-muted">
              Every answer becomes evidence in your knowledge graph.
            </p>
          </div>
          <div>
            <p className="font-mono text-[12px] text-root-cause">Recall</p>
            <p className="mt-1 text-[13px] text-ink-muted">
              The one upstream concept behind your recurring gaps.
            </p>
          </div>
          <div>
            <p className="font-mono text-[12px] text-root-cause">Improve &amp; Forget</p>
            <p className="mt-1 text-[13px] text-ink-muted">
              Memory enriches over time; mastered topics retire.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
