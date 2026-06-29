import { Check, X } from "lucide-react";

import type { AnswerAssessment } from "@/lib/api/schemas";
import { STATE_META, classifyState } from "@/lib/competency";

/** The LLM grade for the most recent answer: score, rationale, and the sub-concepts the
 * answer demonstrated vs missed. Transparent feedback so the score never feels arbitrary. */
export function AssessmentCard({ assessment }: { assessment: AnswerAssessment }) {
  const color = `var(${STATE_META[classifyState(assessment.score)].cssVar})`;

  return (
    <section
      className="rounded-lg border border-border bg-surface p-5 animate-rise-in"
      aria-label="Answer assessment"
    >
      <div className="flex items-center justify-between gap-3">
        <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-ink-subtle">
          Graded · {assessment.concept}
        </p>
        <span
          className="inline-flex items-baseline gap-1 rounded-md border px-2.5 py-1 font-mono text-[13px] font-semibold text-ink"
          style={{
            borderColor: color,
            backgroundColor: `color-mix(in oklch, ${color} 14%, var(--surface-2))`,
          }}
        >
          {assessment.score}
          <span className="text-[11px] font-normal text-ink-muted">/ 5</span>
        </span>
      </div>

      {assessment.rationale && (
        <p className="mt-3 text-[14px] leading-relaxed text-ink-muted">
          {assessment.rationale}
        </p>
      )}

      {(assessment.demonstrated.length > 0 || assessment.missed.length > 0) && (
        <div className="mt-4 flex flex-wrap gap-1.5">
          {assessment.demonstrated.map((item) => (
            <span
              key={`d-${item}`}
              className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[12px] text-ink"
              style={{
                borderColor: "color-mix(in oklch, var(--mastered) 40%, var(--border))",
                backgroundColor: "color-mix(in oklch, var(--mastered) 12%, transparent)",
              }}
            >
              <Check className="h-3 w-3 text-mastered" aria-hidden /> {item}
            </span>
          ))}
          {assessment.missed.map((item) => (
            <span
              key={`m-${item}`}
              className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[12px] text-ink"
              style={{
                borderColor: "color-mix(in oklch, var(--weak) 40%, var(--border))",
                backgroundColor: "color-mix(in oklch, var(--weak) 12%, transparent)",
              }}
            >
              <X className="h-3 w-3 text-weak" aria-hidden /> {item}
            </span>
          ))}
        </div>
      )}
    </section>
  );
}
