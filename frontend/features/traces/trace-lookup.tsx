"use client";

import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";

export function TraceLookup() {
  const router = useRouter();
  const [traceKey, setTraceKey] = useState("");
  const [error, setError] = useState<string>();
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const key = traceKey.trim();
    if (!key) { setError("Enter a trace ID returned with a grounded response."); return; }
    setError(undefined); router.push(`/traces/${encodeURIComponent(key)}`);
  }
  return <section className="max-w-2xl space-y-6"><div><p className="text-sm font-medium text-accent">Traces</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">Open a trace summary.</h1><p className="mt-3 text-muted">Paste a trace ID returned by a grounded query. Only traces owned by the current user and tenant can be opened.</p></div><form className="form-card" onSubmit={submit}><label className="field-label" htmlFor="trace-key">Trace ID</label><div className="mt-4 flex flex-col gap-3 sm:flex-row"><input id="trace-key" className="field-input min-w-0 flex-1 font-mono" value={traceKey} onChange={(event) => setTraceKey(event.target.value)} placeholder="tr_…" autoComplete="off" /><button className="inline-flex w-full shrink-0 items-center justify-center gap-2 rounded border border-accent px-6 py-3 text-sm font-medium text-accent transition hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent sm:w-auto" type="submit">Open trace <span aria-hidden="true">→</span></button></div>{error && <p className="mt-3 text-sm text-danger" role="alert">{error}</p>}</form><p className="rounded-xl border border-line bg-panel p-4 text-sm text-muted shadow-panel">Trace lists, filtering, search, and a tenant-wide explorer need additional backend endpoints and are not available.</p></section>;
}
