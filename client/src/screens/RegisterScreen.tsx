import { zodResolver } from "@hookform/resolvers/zod";
import { CheckCircle2, Loader2 } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { z } from "zod";

import { AuthLayout } from "@/components/auth/AuthLayout";
import {
  AuthTabs,
  FormAlert,
  OrDivider,
  PasswordField,
  SocialButtons,
  TextField,
} from "@/components/auth/fields";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth/AuthProvider";
import type { OAuthProvider } from "@/lib/auth/types";

const schema = z.object({
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(8, "Use at least 8 characters."),
});
type Values = z.infer<typeof schema>;

export function RegisterScreen() {
  const { signUp, signInWithOAuth } = useAuth();
  const navigate = useNavigate();
  const [formError, setFormError] = useState<string | null>(null);
  const [pendingEmail, setPendingEmail] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Values>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = handleSubmit(async (values) => {
    setFormError(null);
    try {
      const { needsEmailConfirmation } = await signUp(values.email, values.password);
      if (needsEmailConfirmation) {
        setPendingEmail(values.email);
      } else {
        navigate("/", { replace: true });
      }
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : "Could not create your account.",
      );
    }
  });

  const onProvider = async (provider: OAuthProvider) => {
    try {
      await signInWithOAuth(provider);
    } catch {
      toast.error(
        `${provider === "google" ? "Google" : "GitHub"} sign-in isn't enabled yet.`,
      );
    }
  };

  if (pendingEmail) {
    return (
      <AuthLayout>
        <div className="animate-rise-in">
          <span className="grid h-11 w-11 place-items-center rounded-full bg-surface-2 text-mastered">
            <CheckCircle2 className="h-6 w-6" aria-hidden />
          </span>
          <h1 className="mt-5 text-2xl font-semibold tracking-tight text-ink">
            Check your inbox
          </h1>
          <p className="mt-2 text-[14px] leading-relaxed text-ink-muted">
            We sent a confirmation link to{" "}
            <span className="font-medium text-ink">{pendingEmail}</span>. Click it to
            activate your account, then log in.
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
      <h1 className="text-2xl font-semibold tracking-tight text-ink">
        Create your account
      </h1>
      <p className="mt-1.5 text-[14px] text-ink-muted">
        Start building a competency graph that remembers you.
      </p>

      <div className="mt-6">
        <AuthTabs active="register" />
      </div>

      <div className="mt-5">
        <SocialButtons onProvider={onProvider} disabled={isSubmitting} />
      </div>
      <OrDivider label="or sign up with email" />

      {formError && (
        <div className="mb-4">
          <FormAlert>{formError}</FormAlert>
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-3.5" noValidate>
        <TextField
          label="Email"
          type="email"
          autoComplete="email"
          placeholder="you@company.com"
          error={errors.email?.message}
          {...register("email")}
        />
        <PasswordField
          label="Password"
          autoComplete="new-password"
          placeholder="At least 8 characters"
          error={errors.password?.message}
          {...register("password")}
        />
        <Button type="submit" size="lg" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> Creating account…
            </>
          ) : (
            "Create account"
          )}
        </Button>
      </form>

      <p className="mt-6 text-center text-[12px] text-ink-subtle">
        By creating an account you agree to the Terms &amp; Privacy Policy.
      </p>
    </AuthLayout>
  );
}
