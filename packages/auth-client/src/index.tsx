"use client";

import { useCallback, useEffect, useRef, useState, type DependencyList } from "react";

export { SessionProvider, useSession, fetchCurrentSession, isMemberUser, type MemberUser, type MemberProfile } from "./session";

/**
 * Small data-loading hook shared by every portal. It keeps the last good value while reloading,
 * ignores results from superseded requests, and exposes reload() for mutations.
 */
export function useAsync<T>(loader: () => Promise<T>, deps: DependencyList = []) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const ticket = useRef(0);

  const reload = useCallback(async () => {
    const current = ++ticket.current;
    setLoading(true);
    try {
      const value = await loader();
      if (current === ticket.current) {
        setData(value);
        setError(null);
      }
    } catch (failure) {
      if (current === ticket.current) setError(failure instanceof Error ? failure.message : "Something went wrong.");
    } finally {
      if (current === ticket.current) setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { data, error, loading, reload, setData };
}

/** Wrap a mutation so components get a busy flag and a user-readable error. */
export function useAction() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const run = useCallback(async <R,>(action: () => Promise<R>): Promise<R | undefined> => {
    setBusy(true);
    setError(null);
    try {
      return await action();
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Something went wrong.");
      return undefined;
    } finally {
      setBusy(false);
    }
  }, []);
  return { busy, error, run, clearError: () => setError(null) };
}
