"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@healthspan/ui/button";
import { Input } from "@healthspan/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { isMemberUser, useSession } from "@/lib/session";

type Feedback = { message: string; error: boolean } | null;

async function submitJson(path: string, values: Record<string, string>) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(values),
  });
  const payload: unknown = await response.json();
  if (!response.ok) {
    const detail =
      typeof payload === "object" && payload !== null && "detail" in payload
        ? String(payload.detail)
        : "Your request could not be completed.";
    throw new Error(detail);
  }
  return payload as Record<string, unknown>;
}

function AuthPage({ children, title }: { children: React.ReactNode; title: string }) {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-lg flex-col justify-center px-4 py-12">
      <Link href="/" className="mb-6 text-center text-sm font-medium text-primary hover:underline">
        Healthspan Network
      </Link>
      <Card className="gap-0 rounded-2xl py-0 shadow-sm">
        <CardHeader className="px-6 pt-6">
          <CardTitle className="text-2xl">{title}</CardTitle>
        </CardHeader>
        <CardContent className="p-6">{children}</CardContent>
      </Card>
    </main>
  );
}

function FeedbackMessage({ feedback }: { feedback: Feedback }) {
  if (!feedback) return null;
  return (
    <p className={feedback.error ? "text-sm text-destructive" : "text-sm text-green-700"} role={feedback.error ? "alert" : "status"}>
      {feedback.message}
    </p>
  );
}

export function LoginForm({ initialMessage }: { initialMessage?: string }) {
  const router = useRouter();
  const { setUser } = useSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [feedback, setFeedback] = useState<Feedback>(
    initialMessage ? { message: initialMessage, error: false } : null,
  );
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (initialMessage) setFeedback({ message: initialMessage, error: false });
  }, [initialMessage]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setFeedback(null);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const payload: unknown = await response.json();
      if (!response.ok) {
        const detail =
          typeof payload === "object" && payload !== null && "detail" in payload
            ? String(payload.detail)
            : "Unable to sign in.";
        throw new Error(detail);
      }
      if (!isMemberUser(payload)) {
        throw new Error("The identity service returned an invalid account.");
      }
      setUser(payload);
      router.replace("/home");
    } catch (submitError) {
      setFeedback({ message: submitError instanceof Error ? submitError.message : "Unable to sign in.", error: true });
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthPage title="Sign in">
      <form className="space-y-4" onSubmit={handleSubmit}>
        <label className="block space-y-2 text-sm font-medium" htmlFor="login-email">
          Email
          <Input autoComplete="email" id="login-email" onChange={(event) => setEmail(event.target.value)} required type="email" value={email} />
        </label>
        <label className="block space-y-2 text-sm font-medium" htmlFor="login-password">
          Password
          <Input autoComplete="current-password" id="login-password" onChange={(event) => setPassword(event.target.value)} required type="password" value={password} />
        </label>
        <FeedbackMessage feedback={feedback} />
        <Button className="w-full" disabled={busy} type="submit">{busy ? "Signing in…" : "Sign in"}</Button>
      </form>
      <div className="mt-5 flex flex-wrap justify-between gap-3 text-sm">
        <Link className="text-primary hover:underline" href="/register">Create an account</Link>
        <Link className="text-primary hover:underline" href="/password-reset">Forgot password?</Link>
      </div>
      <p className="mt-3 text-sm">
        Need to verify your email? <Link className="text-primary hover:underline" href="/verify-email">Resend verification</Link>
      </p>
    </AuthPage>
  );
}

export function RegisterForm() {
  const router = useRouter();
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [feedback, setFeedback] = useState<Feedback>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setFeedback(null);
    try {
      const result = await submitJson("/api/auth/register", {
        display_name: displayName,
        email,
        password,
      });
      const token = typeof result.verification_token === "string" ? result.verification_token : null;
      router.push(token ? `/verify-email?token=${encodeURIComponent(token)}` : "/verify-email");
    } catch (submitError) {
      setFeedback({ message: submitError instanceof Error ? submitError.message : "Unable to create your account.", error: true });
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthPage title="Create your account">
      <form className="space-y-4" onSubmit={handleSubmit}>
        <label className="block space-y-2 text-sm font-medium" htmlFor="register-name">
          Display name
          <Input autoComplete="name" id="register-name" maxLength={120} onChange={(event) => setDisplayName(event.target.value)} required value={displayName} />
        </label>
        <label className="block space-y-2 text-sm font-medium" htmlFor="register-email">
          Email
          <Input autoComplete="email" id="register-email" onChange={(event) => setEmail(event.target.value)} required type="email" value={email} />
        </label>
        <label className="block space-y-2 text-sm font-medium" htmlFor="register-password">
          Password
          <Input autoComplete="new-password" id="register-password" minLength={12} onChange={(event) => setPassword(event.target.value)} required type="password" value={password} />
          <span className="block text-xs font-normal text-muted-foreground">Use at least 12 characters.</span>
        </label>
        <FeedbackMessage feedback={feedback} />
        <Button className="w-full" disabled={busy} type="submit">{busy ? "Creating account…" : "Create account"}</Button>
      </form>
      <p className="mt-5 text-sm">
        Already registered? <Link className="text-primary hover:underline" href="/login">Sign in</Link>
      </p>
    </AuthPage>
  );
}

export function VerifyEmailForm({ initialToken = "" }: { initialToken?: string }) {
  const router = useRouter();
  const [token, setToken] = useState(initialToken);
  const [email, setEmail] = useState("");
  const [feedback, setFeedback] = useState<Feedback>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (initialToken) setToken(initialToken);
  }, [initialToken]);

  async function handleVerify(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setFeedback(null);
    try {
      await submitJson("/api/auth/verify-email", { token });
      router.replace("/login?verified=1");
    } catch (verifyError) {
      setFeedback({ message: verifyError instanceof Error ? verifyError.message : "Unable to verify your email.", error: true });
    } finally {
      setBusy(false);
    }
  }

  async function handleResend() {
    setBusy(true);
    setFeedback(null);
    try {
      const result = await submitJson("/api/auth/resend-verification", { email });
      const resendToken = typeof result.verification_token === "string" ? result.verification_token : null;
      if (resendToken) {
        setToken(resendToken);
        setFeedback({ message: "A development verification token was issued. Submit it above to verify your email.", error: false });
      } else {
        setFeedback({ message: "If the account needs verification, a new link has been sent to its email address.", error: false });
      }
    } catch (resendError) {
      setFeedback({ message: resendError instanceof Error ? resendError.message : "Unable to resend verification.", error: true });
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthPage title="Verify your email">
      <p className="mb-5 text-sm text-muted-foreground">Use the one-time link from your email, or paste its verification token below. Accounts must be verified before sign-in.</p>
      <form className="space-y-4" onSubmit={handleVerify}>
        <label className="block space-y-2 text-sm font-medium" htmlFor="verify-token">
          Verification token
          <Input autoComplete="one-time-code" id="verify-token" onChange={(event) => setToken(event.target.value)} required value={token} />
        </label>
        <FeedbackMessage feedback={feedback} />
        <Button className="w-full" disabled={busy || !token.trim()} type="submit">{busy ? "Verifying…" : "Verify email"}</Button>
      </form>
      <div className="mt-6 border-t pt-5">
        <label className="block space-y-2 text-sm font-medium" htmlFor="resend-email">
          Send a new verification link
          <Input autoComplete="email" id="resend-email" onChange={(event) => setEmail(event.target.value)} type="email" value={email} />
        </label>
        <Button className="mt-3 w-full" disabled={busy || !email} onClick={handleResend} type="button" variant="outline">Resend verification</Button>
      </div>
      <p className="mt-5 text-sm"><Link className="text-primary hover:underline" href="/login">Back to sign in</Link></p>
    </AuthPage>
  );
}

export function PasswordResetForm({ initialToken = "" }: { initialToken?: string }) {
  const [email, setEmail] = useState("");
  const [token, setToken] = useState(initialToken);
  const [newPassword, setNewPassword] = useState("");
  const [feedback, setFeedback] = useState<Feedback>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (initialToken) setToken(initialToken);
  }, [initialToken]);

  async function requestReset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setFeedback(null);
    try {
      const result = await submitJson("/api/auth/password-reset", { email });
      const resetToken = typeof result.reset_token === "string" ? result.reset_token : null;
      if (resetToken) {
        setToken(resetToken);
        setFeedback({ message: "A development reset token was issued. Set your new password below.", error: false });
      } else {
        setFeedback({ message: "If an account exists for this address, password-reset instructions have been sent.", error: false });
      }
    } catch (resetError) {
      setFeedback({ message: resetError instanceof Error ? resetError.message : "Unable to request a password reset.", error: true });
    } finally {
      setBusy(false);
    }
  }

  async function confirmReset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setFeedback(null);
    try {
      await submitJson("/api/auth/password-reset-confirm", { token, new_password: newPassword });
      setFeedback({ message: "Your password was updated. Sign in with your new password.", error: false });
      setToken("");
      setNewPassword("");
    } catch (resetError) {
      setFeedback({ message: resetError instanceof Error ? resetError.message : "Unable to reset your password.", error: true });
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthPage title="Reset your password">
      <p className="mb-5 text-sm text-muted-foreground">Request a one-time reset link, then choose a new password. Existing sessions are revoked when the password changes.</p>
      <form className="space-y-4" onSubmit={requestReset}>
        <label className="block space-y-2 text-sm font-medium" htmlFor="reset-email">
          Account email
          <Input autoComplete="email" id="reset-email" onChange={(event) => setEmail(event.target.value)} required type="email" value={email} />
        </label>
        <Button className="w-full" disabled={busy} type="submit">Send reset instructions</Button>
      </form>
      {token && (
        <form className="mt-6 space-y-4 border-t pt-5" onSubmit={confirmReset}>
          <label className="block space-y-2 text-sm font-medium" htmlFor="reset-token">
            Reset token
            <Input autoComplete="one-time-code" id="reset-token" onChange={(event) => setToken(event.target.value)} required value={token} />
          </label>
          <label className="block space-y-2 text-sm font-medium" htmlFor="reset-new-password">
            New password
            <Input autoComplete="new-password" id="reset-new-password" minLength={12} onChange={(event) => setNewPassword(event.target.value)} required type="password" value={newPassword} />
          </label>
          <Button className="w-full" disabled={busy} type="submit">Update password</Button>
        </form>
      )}
      <div className="mt-4"><FeedbackMessage feedback={feedback} /></div>
      <p className="mt-5 text-sm"><Link className="text-primary hover:underline" href="/login">Back to sign in</Link></p>
    </AuthPage>
  );
}
