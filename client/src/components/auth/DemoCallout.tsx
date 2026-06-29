import { Loader2 } from "lucide-react";

/** The sandboxed-demo affordance. The demo is a real authenticated user with isolated
 * data — not an auth bypass. */
export function DemoCallout({
  onDemo,
  pending,
  disabled,
}: {
  onDemo: () => void;
  pending: boolean;
  disabled?: boolean;
}) {
  return (
    <div className="rounded-md border border-border bg-surface px-4 py-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[13px] font-medium text-ink">Just exploring?</p>
          <p className="text-[12px] text-ink-subtle">
            Jump into a sandboxed demo account.
          </p>
        </div>
        <button
          type="button"
          onClick={onDemo}
          disabled={disabled || pending}
          className="inline-flex h-9 shrink-0 items-center gap-2 rounded-md border border-border bg-surface-2 px-3 text-[13px] text-ink transition-colors hover:border-border-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-60"
        >
          {pending ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden />
          ) : (
            <span className="relative flex h-1.5 w-1.5" aria-hidden>
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-root-cause opacity-60" />
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-root-cause" />
            </span>
          )}
          Try the demo
        </button>
      </div>
    </div>
  );
}
