import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
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
import { DemoCallout } from "@/components/auth/DemoCallout";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth/AuthProvider";
import type { OAuthProvider } from "@/lib/auth/types";

const schema = z.object({
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(1, "Enter your password."),
});
type Values = z.infer<typeof schema>;

export function LoginScreen() {
  const { signIn, signInWithDemo, signInWithOAuth, hasDemo } = useAuth();
  const navigate = useNavigate();
  const [formError, setFormError] = useState<string | null>(null);
  const [demoPending, setDemoPending] = useState(false);
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
      await signIn(values.email, values.password);
      navigate("/", { replace: true });
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Could not sign in.");
    }
  });

  const onDemo = async () => {
    setFormError(null);
    setDemoPending(true);
    try {
      await signInWithDemo();
      navigate("/", { replace: true });
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "The demo is unavailable.");
    } finally {
      setDemoPending(false);
    }
  };

  const onProvider = async (provider: OAuthProvider) => {
    try {
      await signInWithOAuth(provider);
    } catch {
      toast.error(
        `${provider === "google" ? "Google" : "GitHub"} sign-in isn't enabled yet.`,
      );
    }
  };

  const busy = isSubmitting || demoPending;

  return (
    <AuthLayout>
      <h1 className="text-2xl font-semibold tracking-tight text-ink">Welcome back</h1>
      <p className="mt-1.5 text-[14px] text-ink-muted">
        Log in to continue building your competency graph.
      </p>

      <div className="mt-6">
        <AuthTabs active="login" />
      </div>

      <div className="mt-5">
        <SocialButtons onProvider={onProvider} disabled={busy} />
      </div>
      <OrDivider />

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
          autoComplete="current-password"
          placeholder="••••••••"
          error={errors.password?.message}
          hint={
            <Link
              to="/forgot-password"
              className="text-[12px] text-primary hover:underline"
            >
              Forgot password?
            </Link>
          }
          {...register("password")}
        />
        <Button type="submit" size="lg" className="w-full" disabled={busy}>
          {isSubmitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> Signing in…
            </>
          ) : (
            "Log in"
          )}
        </Button>
      </form>

      {hasDemo && (
        <div className="mt-5">
          <DemoCallout onDemo={onDemo} pending={demoPending} disabled={busy} />
        </div>
      )}

      <p className="mt-6 text-center text-[12px] text-ink-subtle">
        By continuing you agree to the Terms &amp; Privacy Policy.
      </p>
    </AuthLayout>
  );
}
