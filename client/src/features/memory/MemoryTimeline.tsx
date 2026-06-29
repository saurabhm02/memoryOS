import type { MemorySnapshot } from "./memoryHistory";

function Distribution({ s }: { s: MemorySnapshot }) {
  const total = s.unvisited + s.weak + s.medium + s.mastered || 1;
  const segment = (count: number, cssVar: string) =>
    count > 0 ? (
      <span
        className="block h-1.5"
        style={{ width: `${(count / total) * 100}%`, background: `var(${cssVar})` }}
      />
    ) : null;
  return (
    <div className="flex h-1.5 w-full overflow-hidden rounded-full bg-surface-2">
      {segment(s.mastered, "--mastered")}
      {segment(s.medium, "--medium")}
      {segment(s.weak, "--weak")}
      {segment(s.unvisited, "--unvisited")}
    </div>
  );
}

export function MemoryTimeline({ history }: { history: MemorySnapshot[] }) {
  if (history.length <= 1) {
    return (
      <section className="rounded-lg border border-border bg-surface p-5">
        <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-ink-subtle">
          Memory timeline
        </p>
        <p className="mt-3 max-w-prose text-sm text-ink-muted">
          Your timeline grows as you practice. Come back after another session to watch
          your memory evolve — concepts filling in, and the root cause emerging.
        </p>
      </section>
    );
  }

  let patternShown = false;
  return (
    <section className="rounded-lg border border-border bg-surface p-5">
      <div className="flex items-center justify-between">
        <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-ink-subtle">
          Memory timeline
        </p>
        <p className="text-[12px] text-ink-muted">{history.length} snapshots</p>
      </div>
      <ol className="mt-5 flex items-stretch gap-3 overflow-x-auto pb-2">
        {history.map((snapshot, i) => {
          const firstPattern = !patternShown && snapshot.rootCause !== null;
          if (firstPattern) patternShown = true;
          return (
            <li key={snapshot.at} className="min-w-[148px] flex-1">
              <Distribution s={snapshot} />
              <p className="mt-3 text-sm font-medium text-ink">Snapshot {i + 1}</p>
              <p className="text-[12px] text-ink-subtle">
                {snapshot.mastered} mastered · {snapshot.weak} weak
              </p>
              {firstPattern && (
                <p
                  className="mt-1 font-mono text-[11px]"
                  style={{ color: "var(--pattern)" }}
                >
                  ✦ Root cause: {snapshot.rootCause}
                </p>
              )}
            </li>
          );
        })}
      </ol>
    </section>
  );
}
