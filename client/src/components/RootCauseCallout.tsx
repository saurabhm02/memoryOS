import { ArrowRight } from "lucide-react";

import { cn } from "@/lib/utils";

import { ConceptChip } from "./ConceptChip";

interface RootCauseCalloutProps {
  rootCause: string;
  resolves: string[];
  narration?: string | null;
  className?: string;
}

function joinConcepts(items: string[]): string {
  if (items.length <= 1) return items[0] ?? "";
  if (items.length === 2) return `${items[0]} and ${items[1]}`;
  return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`;
}

/**
 * The primary product insight, stated plainly: several recurring weaknesses converge on
 * one upstream concept. This leads every screen; the graph explains it visually.
 */
export function RootCauseCallout({
  rootCause,
  resolves,
  narration,
  className,
}: RootCauseCalloutProps) {
  return (
    <section
      aria-labelledby="root-cause-title"
      className={cn(
        "animate-rise-in rounded-lg border bg-root-cause-bg p-5 sm:p-6",
        className,
      )}
      style={{ borderColor: "color-mix(in oklch, var(--root-cause) 35%, var(--border))" }}
    >
      <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-root-cause">
        Root cause
      </p>

      <h2
        id="root-cause-title"
        className="mt-2 text-balance text-xl font-semibold leading-snug text-ink sm:text-2xl"
      >
        {resolves.length > 0 ? (
          <>
            {joinConcepts(resolves)} all build on{" "}
            <span className="text-root-cause">{rootCause}</span>.
          </>
        ) : (
          <>
            Your next focus is <span className="text-root-cause">{rootCause}</span>.
          </>
        )}
      </h2>

      {resolves.length > 0 && (
        <div className="mt-4 flex flex-wrap items-center gap-2">
          {resolves.map((concept) => (
            <ConceptChip key={concept} concept={concept} tone="weak" />
          ))}
          <ArrowRight className="h-4 w-4 shrink-0 text-ink-subtle" aria-hidden />
          <ConceptChip concept={rootCause} tone="root-cause" />
        </div>
      )}

      {narration && (
        <p className="mt-4 max-w-prose text-pretty text-sm leading-relaxed text-ink-muted">
          {narration}
        </p>
      )}
    </section>
  );
}
