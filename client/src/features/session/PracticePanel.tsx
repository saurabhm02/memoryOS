import { useState } from "react";

import { RememberingIndicator } from "@/components/RememberingIndicator";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface PracticePanelProps {
  concept: string;
  question: string;
  isPending: boolean;
  onSubmit: (answer: string) => void;
  className?: string;
}

/** The session's answer flow: a focused question and a free-text answer. Submitting sends
 * the answer to an interviewer-style model that grades it 0–5; the panel shows the calm
 * "remembering" affordance while the grade is produced and Cognee writes. */
export function PracticePanel({
  concept,
  question,
  isPending,
  onSubmit,
  className,
}: PracticePanelProps) {
  const [answer, setAnswer] = useState("");
  const canSubmit = answer.trim().length > 0 && !isPending;

  return (
    <section
      className={cn(
        "flex flex-col rounded-lg border border-border bg-surface p-5",
        className,
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-ink-subtle">
          Practice
        </p>
        <span className="inline-flex items-center gap-1.5 rounded-full border border-border px-2.5 py-1 font-mono text-[12px] text-ink-muted">
          Focus · {concept}
        </span>
      </div>

      <p className="mt-3 text-[15px] leading-relaxed text-ink">{question}</p>

      <textarea
        value={answer}
        onChange={(event) => setAnswer(event.target.value)}
        disabled={isPending}
        aria-label="Your answer"
        placeholder="Type your answer — an interviewer-style model will grade it…"
        className="mt-3 min-h-[140px] w-full resize-none rounded-md border border-border bg-surface-2 p-3 text-[14px] leading-relaxed text-ink placeholder:text-ink-subtle focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-60"
      />

      <div className="mt-auto flex flex-wrap items-center justify-between gap-3 pt-5">
        {isPending ? (
          <RememberingIndicator />
        ) : (
          <span className="text-[13px] text-ink-subtle">
            Graded 0–5 against the concept — your memory builds on the result.
          </span>
        )}
        <Button onClick={() => canSubmit && onSubmit(answer)} disabled={!canSubmit}>
          Submit answer
        </Button>
      </div>
    </section>
  );
}
