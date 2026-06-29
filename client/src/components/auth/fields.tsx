import { AlertCircle, CheckCircle2, Eye, EyeOff, Github } from "lucide-react";
import { forwardRef, useState, type InputHTMLAttributes, type ReactNode } from "react";
import { NavLink } from "react-router-dom";

import { cn } from "@/lib/utils";

const inputBase =
  "h-11 w-full rounded-md border bg-surface-2 text-sm text-ink placeholder:text-ink-subtle transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-bg disabled:opacity-60";

interface FieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: ReactNode;
}

export const TextField = forwardRef<HTMLInputElement, FieldProps>(
  ({ label, error, hint, id, name, className, ...props }, ref) => {
    const fieldId = id ?? name;
    return (
      <div>
        <div className="mb-1.5 flex items-center justify-between">
          <label htmlFor={fieldId} className="text-[13px] text-ink-muted">
            {label}
          </label>
          {hint}
        </div>
        <input
          id={fieldId}
          name={name}
          ref={ref}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? `${fieldId}-error` : undefined}
          className={cn(
            inputBase,
            "px-3",
            error ? "border-danger" : "border-border",
            className,
          )}
          {...props}
        />
        {error && (
          <p id={`${fieldId}-error`} className="mt-1.5 text-[12px] text-danger">
            {error}
          </p>
        )}
      </div>
    );
  },
);
TextField.displayName = "TextField";

export const PasswordField = forwardRef<HTMLInputElement, FieldProps>(
  ({ label, error, hint, id, name, className, ...props }, ref) => {
    const [show, setShow] = useState(false);
    const fieldId = id ?? name;
    return (
      <div>
        <div className="mb-1.5 flex items-center justify-between">
          <label htmlFor={fieldId} className="text-[13px] text-ink-muted">
            {label}
          </label>
          {hint}
        </div>
        <div className="relative">
          <input
            id={fieldId}
            name={name}
            ref={ref}
            type={show ? "text" : "password"}
            aria-invalid={error ? true : undefined}
            aria-describedby={error ? `${fieldId}-error` : undefined}
            className={cn(
              inputBase,
              "pl-3 pr-10",
              error ? "border-danger" : "border-border",
              className,
            )}
            {...props}
          />
          <button
            type="button"
            onClick={() => setShow((s) => !s)}
            aria-label={show ? "Hide password" : "Show password"}
            aria-pressed={show}
            className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded p-1.5 text-ink-subtle transition-colors hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          >
            {show ? (
              <EyeOff className="h-4 w-4" aria-hidden />
            ) : (
              <Eye className="h-4 w-4" aria-hidden />
            )}
          </button>
        </div>
        {error && (
          <p id={`${fieldId}-error`} className="mt-1.5 text-[12px] text-danger">
            {error}
          </p>
        )}
      </div>
    );
  },
);
PasswordField.displayName = "PasswordField";

type AlertVariant = "error" | "success" | "info";

const ALERT_TINT: Record<AlertVariant, { var: string; Icon: typeof AlertCircle }> = {
  error: { var: "--danger", Icon: AlertCircle },
  success: { var: "--success", Icon: CheckCircle2 },
  info: { var: "--primary", Icon: AlertCircle },
};

export function FormAlert({
  variant = "error",
  children,
}: {
  variant?: AlertVariant;
  children: ReactNode;
}) {
  const { var: token, Icon } = ALERT_TINT[variant];
  return (
    <div
      role="alert"
      className="flex items-start gap-2 rounded-md border px-3 py-2.5 text-[13px] text-ink animate-fade-in"
      style={{
        borderColor: `color-mix(in oklch, var(${token}) 40%, var(--border))`,
        background: `color-mix(in oklch, var(${token}) 10%, transparent)`,
      }}
    >
      <Icon
        className="mt-0.5 h-4 w-4 flex-none"
        style={{ color: `var(${token})` }}
        aria-hidden
      />
      <span className="text-ink-muted">{children}</span>
    </div>
  );
}

export function OrDivider({ label = "or continue with email" }: { label?: string }) {
  return (
    <div className="my-5 flex items-center gap-3 text-[12px] text-ink-subtle">
      <span className="h-px flex-1 bg-border" />
      {label}
      <span className="h-px flex-1 bg-border" />
    </div>
  );
}

function GoogleGlyph() {
  return (
    <svg className="h-4 w-4" viewBox="0 0 24 24" aria-hidden>
      <path
        fill="#EA4335"
        d="M12 10.2v3.9h5.5c-.24 1.4-1.7 4.1-5.5 4.1a6.2 6.2 0 0 1 0-12.4c1.9 0 3.2.8 3.9 1.5l2.7-2.6C16.9 2.9 14.7 2 12 2a10 10 0 1 0 0 20c5.8 0 9.6-4 9.6-9.7 0-.7 0-1.1-.1-1.6H12z"
      />
    </svg>
  );
}

/** Social providers are placeholders until enabled in Supabase; clicking surfaces a clear
 * message rather than failing silently. */
export function SocialButtons({
  onProvider,
  disabled,
}: {
  onProvider: (provider: "google" | "github") => void;
  disabled?: boolean;
}) {
  const base =
    "inline-flex h-10 items-center justify-center gap-2 rounded-md border border-border bg-surface text-[13px] text-ink transition-colors hover:border-border-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-60";
  return (
    <div className="grid grid-cols-2 gap-2">
      <button
        type="button"
        className={base}
        onClick={() => onProvider("google")}
        disabled={disabled}
      >
        <GoogleGlyph /> Google
      </button>
      <button
        type="button"
        className={base}
        onClick={() => onProvider("github")}
        disabled={disabled}
      >
        <Github className="h-4 w-4" aria-hidden /> GitHub
      </button>
    </div>
  );
}

export function AuthTabs({ active }: { active: "login" | "register" }) {
  const tab = (to: string, label: string, key: "login" | "register") => (
    <NavLink
      to={to}
      className={cn(
        "rounded-[6px] py-1.5 text-center text-[13px] transition-colors",
        active === key
          ? "bg-surface-2 font-medium text-ink"
          : "text-ink-muted hover:text-ink",
      )}
    >
      {label}
    </NavLink>
  );
  return (
    <div className="grid grid-cols-2 gap-1 rounded-md border border-border bg-surface p-1">
      {tab("/login", "Log in", "login")}
      {tab("/register", "Create account", "register")}
    </div>
  );
}
