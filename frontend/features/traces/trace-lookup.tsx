"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export function TraceLookup() {
  const router = useRouter();
  const [traceKey, setTraceKey] = useState("");
  const [error, setError] = useState<string>();
  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const key = traceKey.trim();
    if (!key) { setError("Enter a trace ID returned with a grounded response."); return; }
    setError(undefined); router.push(`/traces/${encodeURIComponent(key)}`);
  }
  return <section className="max-w-2xl space-y-6"><div><p className="text-sm font-medium text-accent">Trace explorer · F6</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">Open a trace summary.</h1><p className="mt-3 text-muted">Paste a trace ID returned by a grounded query. Only traces owned by the current user and tenant can be opened.</p></div><form className="rounded-lg border border-line bg-panel p-5 shadow-panel" onSubmit={submit}><label className="block text-sm font-medium" htmlFor="trace-key">Trace ID</label><input id="trace-key" className="mt-2 w-full rounded border border-line p-2 font-mono text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent" value={traceKey} onChange={(event) => setTraceKey(event.target.value)} placeholder="tr_…" autoComplete="off" />{error && <p className="mt-3 text-sm text-danger" role="alert">{error}</p>}<button className="mt-4 rounded bg-accent px-3 py-2 text-sm font-medium text-white hover:bg-accent-strong" type="submit">Open trace</button></form><p className="rounded-lg border border-line bg-panel p-4 text-sm text-muted">Trace lists, filtering, search, and a tenant-wide explorer need additional backend endpoints and are not available.</p></section>;
}
