import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Loader2, MailCheck } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";

import { AuthLayout } from "@/components/auth/AuthLayout";
import { FormAlert, TextField } from "@/components/auth/fields";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth/AuthProvider";

const schema = z.object({ email: z.string().email("Enter a valid email address.") });
type Values = z.infer<typeof schema>;

export function ForgotPasswordScreen() {
  const { resetPassword } = useAuth();
  const [sentTo, setSentTo] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Values>({ resolver: zodResolver(schema), defaultValues: { email: "" } });

  const onSubmit = handleSubmit(async (values) => {
    setFormError(null);
    try {
      await resetPassword(values.email);
      setSentTo(values.email);
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Could not send the email.");
    }
  });

  if (sentTo) {
    return (
      <AuthLayout>
        <div className="animate-rise-in">
          <span className="grid h-11 w-11 place-items-center rounded-full bg-surface-2 text-mastered">
            <MailCheck className="h-6 w-6" aria-hidden />
          </span>
          <h1 className="mt-5 text-2xl font-semibold tracking-tight text-ink">
            Check your inbox
          </h1>
          <p className="mt-2 text-[14px] leading-relaxed text-ink-muted">
            If an account exists for{" "}
            <span className="font-medium text-ink">{sentTo}</span>, a password-reset link
            is on its way.
          </p>
          <Button asChild size="lg" className="mt-6 w-full">
            <Link to="/login">Back to log in</Link>
          </Button>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout>
      <Link
        to="/login"
        className="mb-6 inline-flex items-center gap-1.5 text-[13px] text-ink-muted hover:text-ink"
      >
        <ArrowLeft className="h-3.5 w-3.5" aria-hidden /> Back to log in
      </Link>
      <h1 className="text-2xl font-semibold tracking-tight text-ink">
        Reset your password
      </h1>
      <p className="mt-1.5 text-[14px] text-ink-muted">
        Enter your email and we'll send you a reset link.
      </p>

      {formError && (
        <div className="mt-5">
          <FormAlert>{formError}</FormAlert>
        </div>
      )}

      <form onSubmit={onSubmit} className="mt-5 space-y-3.5" noValidate>
        <TextField
          label="Email"
          type="email"
          autoComplete="email"
          placeholder="you@company.com"
          error={errors.email?.message}
          {...register("email")}
        />
        <Button type="submit" size="lg" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> Sending…
            </>
          ) : (
            "Send reset link"
          )}
        </Button>
      </form>
    </AuthLayout>
  );
}
