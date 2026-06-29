import { cn } from "@/lib/utils";

interface RememberingIndicatorProps {
  label?: string;
  className?: string;
}

/**
 * The calm "Cognee is remembering…" affordance shown during the live ~20–40s write.
 * Never a blocking spinner. Announced politely to assistive tech; the ping animation is
 * suppressed under prefers-reduced-motion by the global guard in index.css.
 */
export function RememberingIndicator({
  label = "Cognee is remembering",
  className,
}: RememberingIndicatorProps) {
  return (
    <span
      role="status"
      aria-live="polite"
      className={cn(
        "inline-flex items-center gap-2 text-[13px] text-ink-muted",
        className,
      )}
    >
      <span className="relative flex h-2 w-2" aria-hidden>
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-60" />
        <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
      </span>
      {label}…
    </span>
  );
}
