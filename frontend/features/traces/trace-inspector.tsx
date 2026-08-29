"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { CopyValueButton } from "@/components/copy-value-button";
import { api, type ApiError } from "@/lib/api/client";

export function TraceInspector({ traceId, initiallyOpen = false }: Readonly<{ traceId: string; initiallyOpen?: boolean }>) {
  const [open, setOpen] = useState(initiallyOpen);
  const trace = useQuery({ queryKey: ["trace", traceId], queryFn: () => api.trace(traceId), enabled: open, retry: 1 });
  return <section className="rounded-lg border border-line bg-panel p-5 shadow-panel"><div className="flex flex-wrap items-center justify-between gap-3"><div><h3 className="font-semibold">RAG inspector</h3><p className="mt-1 text-sm text-muted">Inspect the sanitized summary recorded for this response.</p></div><button className="rounded border border-accent px-3 py-2 text-sm font-medium text-accent hover:bg-slate-50" type="button" onClick={() => setOpen((value) => !value)} aria-expanded={open}>{open ? "Hide inspector" : "Inspect trace"}</button></div>
    {open && <div className="mt-5 border-t border-line pt-5">{trace.isPending && <p className="text-sm text-muted" role="status">Loading trace summary…</p>}{trace.isError && <TraceError error={trace.error as unknown as ApiError} retry={() => void trace.refetch()} />}{trace.data && <TraceDetails trace={trace.data} />}</div>}
  </section>;
}

function TraceError({ error, retry }: Readonly<{ error: ApiError; retry: () => void }>) {
  const message = error.status === 404 ? "This trace is not available to the current development identity." : error.message;
  return <div><p className="text-sm text-danger" role="alert">{message}</p>{error.retryable && <button className="mt-3 rounded border border-accent px-3 py-2 text-sm font-medium text-accent" type="button" onClick={retry}>Retry</button>}</div>;
}

function TraceDetails({ trace }: Readonly<{ trace: Awaited<ReturnType<typeof api.trace>> }>) {
  return <div className="space-y-5"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-sm text-muted">Trace ID</p><div className="mt-1 flex flex-wrap gap-2"><code className="break-all text-xs">{trace.trace_id}</code><CopyValueButton value={trace.trace_id} /></div></div><dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm"><div><dt className="text-muted">Outcome</dt><dd className="mt-1 capitalize">{trace.outcome}</dd></div><div><dt className="text-muted">Latency</dt><dd className="mt-1">{trace.latency_ms} ms</dd></div></dl></div>
    <div className="grid gap-5 md:grid-cols-2"><section><h4 className="text-sm font-semibold">Retrieval events</h4>{trace.retrieval_events.length === 0 ? <p className="mt-2 text-sm text-muted">No retrieval events were recorded.</p> : <ol className="mt-3 space-y-3 border-l border-line pl-4">{trace.retrieval_events.map((event, index) => <li key={`${event.stage}-${index}`} className="text-sm"><p className="font-medium capitalize">{event.stage}</p><p className="text-muted">{event.output_count} outputs · {event.latency_ms} ms</p></li>)}</ol>}</section><section><h4 className="text-sm font-semibold">Security events</h4>{trace.security_events.length === 0 ? <p className="mt-2 text-sm text-muted">No non-allow security events were recorded.</p> : <ol className="mt-3 space-y-3 border-l border-line pl-4">{trace.security_events.map((event, index) => <li key={`${event.stage}-${index}`} className="text-sm"><p className="font-medium capitalize">{event.stage} · {event.action}</p><p className="text-muted">{event.risk} risk{event.categories.length ? ` · ${event.categories.join(", ")}` : ""}</p></li>)}</ol>}</section></div>
    <p className="rounded bg-slate-50 p-3 text-xs text-muted">This summary does not include raw document text, retrieval candidates or scores, selected context, prompt content, model usage, or a trace-history list.</p>
  </div>;
}
