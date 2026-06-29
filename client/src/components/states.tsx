import { AlertTriangle, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { Button } from "./ui/button";

export function ErrorState({
  message = "Something went wrong reaching the server.",
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div role="alert" className="grid h-full place-items-center p-6 text-center">
      <div className="max-w-sm">
        <AlertTriangle className="mx-auto h-6 w-6 text-danger" aria-hidden />
        <p className="mt-3 text-sm text-ink-muted">{message}</p>
        {onRetry && (
          <Button variant="secondary" size="sm" className="mt-4" onClick={onRetry}>
            Try again
          </Button>
        )}
      </div>
    </div>
  );
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon?: LucideIcon;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="grid place-items-center rounded-lg border border-border bg-surface p-8 text-center">
      <div className="max-w-md">
        {Icon && (
          <span className="mx-auto grid h-10 w-10 place-items-center rounded-lg bg-surface-2 text-ink-muted">
            <Icon className="h-5 w-5" aria-hidden />
          </span>
        )}
        <h2 className="mt-4 text-balance text-lg font-semibold text-ink">{title}</h2>
        <p className="mx-auto mt-2 max-w-prose text-pretty text-sm leading-relaxed text-ink-muted">
          {description}
        </p>
        {action && <div className="mt-5 flex justify-center">{action}</div>}
      </div>
    </div>
  );
}
