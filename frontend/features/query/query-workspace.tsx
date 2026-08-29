"use client";

import { useMutation } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { z } from "zod";
import { CopyValueButton } from "@/components/copy-value-button";
import { api, type ApiError } from "@/lib/api/client";
import { queryRequestSchema, type QueryResponse } from "@/lib/api/schemas";

const uuidSchema = z.string().uuid();

function Result({ result }: Readonly<{ result: QueryResponse }>) {
  const events = result.security.events as Array<{ stage?: string; risk?: string; action?: string; categories?: string[] }>;
  return <section className="space-y-4" aria-live="polite"><div className="rounded-lg border border-line bg-panel p-5 shadow-panel"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-sm font-medium text-accent">Grounded response</p><h2 className="mt-1 text-xl font-semibold">{result.answerability.status === "answerable" ? "Answer supported by retrieved evidence" : "Evidence may be insufficient"}</h2></div><span className="rounded bg-slate-100 px-2 py-1 text-sm">Confidence {Math.round(result.answerability.confidence * 100)}%</span></div><p className="mt-4 whitespace-pre-wrap leading-7">{result.answer}</p></div>
    <div className="grid gap-4 md:grid-cols-2"><section className="rounded-lg border border-line bg-panel p-5 shadow-panel"><h3 className="font-semibold">Citations</h3>{result.citations.length === 0 ? <p className="mt-2 text-sm text-muted">No citations were returned.</p> : <ol className="mt-3 space-y-3">{result.citations.map((citation) => <li key={citation.id} className="text-sm"><p className="font-medium">[{citation.id}] {citation.filename}</p><p className="mt-1 text-muted">{citation.section ?? "No section"}{citation.page !== null ? ` · page ${citation.page}` : ""}</p><p className="mt-1 break-all font-mono text-xs text-muted">{citation.document_id}</p></li>)}</ol>}</section>
      <section className="rounded-lg border border-line bg-panel p-5 shadow-panel"><h3 className="font-semibold">Response details</h3><dl className="mt-3 space-y-2 text-sm"><div className="flex justify-between gap-4"><dt className="text-muted">Context chunks</dt><dd>{result.usage.context_chunks}</dd></div><div className="flex justify-between gap-4"><dt className="text-muted">Dense candidates</dt><dd>{result.usage.dense_candidates}</dd></div><div className="flex justify-between gap-4"><dt className="text-muted">Sparse candidates</dt><dd>{result.usage.sparse_candidates}</dd></div></dl><div className="mt-4"><p className="text-sm text-muted">Trace ID</p><div className="mt-1 flex flex-wrap gap-2"><code className="break-all text-xs">{result.trace_id}</code><CopyValueButton value={result.trace_id} /></div></div></section></div>
    <section className="rounded-lg border border-line bg-panel p-5 shadow-panel"><h3 className="font-semibold">Security</h3><p className="mt-2 text-sm">Action: <strong className="capitalize">{result.security.action}</strong></p>{events.length > 0 && <ul className="mt-2 list-disc pl-5 text-sm text-muted">{events.map((event, index) => <li key={`${event.stage}-${index}`}>{event.stage ?? "Scan"}: {event.action ?? "reported"}{event.categories?.length ? ` (${event.categories.join(", ")})` : ""}</li>)}</ul>}{events.length === 0 && <p className="mt-2 text-sm text-muted">No security events were returned.</p>}</section>
    {result.rewritten_queries.length > 0 && <details className="rounded-lg border border-line bg-panel p-5 shadow-panel"><summary className="cursor-pointer font-semibold">Rewritten retrieval queries</summary><ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-muted">{result.rewritten_queries.map((query) => <li key={query}>{query}</li>)}</ul></details>}
  </section>;
}

export function QueryWorkspace() {
  const controller = useRef<AbortController | undefined>(undefined);
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(8);
  const [documentIds, setDocumentIds] = useState("");
  const [transform, setTransform] = useState(false);
  const [rerank, setRerank] = useState(false);
  const [formError, setFormError] = useState<string>();
  const [cancelled, setCancelled] = useState(false);
  const ask = useMutation({ mutationFn: ({ payload, signal }: { payload: z.infer<typeof queryRequestSchema>; signal: AbortSignal }) => api.ask(payload, signal) });
  const apiError = ask.error as unknown as ApiError | null;

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const ids = documentIds.split(/[\s,]+/).filter(Boolean);
    if (ids.some((id) => !uuidSchema.safeParse(id).success)) { setFormError("Each document filter must be a valid UUID."); return; }
    const parsed = queryRequestSchema.safeParse({ query: query.trim(), top_k: topK, document_ids: ids, transform, rerank });
    if (!parsed.success) { setFormError("Enter a question and choose a retrieval count from 1 to 20."); return; }
    controller.current = new AbortController(); setCancelled(false); setFormError(undefined); ask.mutate({ payload: parsed.data, signal: controller.current.signal });
  }
  function cancel() { controller.current?.abort(); setCancelled(true); }

  return <div className="max-w-4xl space-y-6"><div><p className="text-sm font-medium text-accent">Grounded chat · F3</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">Ask a grounded question.</h1><p className="mt-3 text-muted">This sends one buffered request and returns the completed answer with its citations. It does not provide message streaming or conversation history.</p></div>
    <form className="rounded-lg border border-line bg-panel p-5 shadow-panel" onSubmit={submit}><label className="block text-sm font-medium" htmlFor="query">Question</label><textarea id="query" value={query} onChange={(event) => setQuery(event.target.value)} className="mt-2 min-h-32 w-full rounded border border-line p-3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent" placeholder="Ask about documents available to your tenant." required disabled={ask.isPending} />
      <div className="mt-4 grid gap-4 sm:grid-cols-2"><label className="text-sm font-medium">Retrieval count <input className="mt-1 block w-full rounded border border-line p-2" type="number" min="1" max="20" value={topK} onChange={(event) => setTopK(Number(event.target.value))} disabled={ask.isPending} /></label><label className="text-sm font-medium">Document ID filters <input className="mt-1 block w-full rounded border border-line p-2" value={documentIds} onChange={(event) => setDocumentIds(event.target.value)} placeholder="UUIDs, comma-separated" disabled={ask.isPending} /></label></div>
      <div className="mt-4 flex flex-wrap gap-5"><label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={transform} onChange={(event) => setTransform(event.target.checked)} disabled={ask.isPending} /> Transform query</label><label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={rerank} onChange={(event) => setRerank(event.target.checked)} disabled={ask.isPending} /> Rerank results</label></div>
      {formError && <p className="mt-3 text-sm text-danger" role="alert">{formError}</p>}{ask.isError && !cancelled && <p className="mt-3 text-sm text-danger" role="alert">{apiError?.status === 403 ? "This request was blocked by policy. Your question is not repeated here." : apiError?.status === 503 ? "The generation provider is unavailable. You can retry later." : apiError?.message ?? "The query could not be completed."}</p>}{cancelled && <p className="mt-3 text-sm text-muted" role="status">Request cancelled locally.</p>}
      <div className="mt-5 flex gap-3"><button className="rounded bg-accent px-3 py-2 text-sm font-medium text-white hover:bg-accent-strong disabled:cursor-not-allowed disabled:opacity-60" disabled={ask.isPending}>{ask.isPending ? "Generating…" : "Ask question"}</button>{ask.isPending && <button className="rounded border border-line px-3 py-2 text-sm font-medium hover:bg-slate-50" type="button" onClick={cancel}>Cancel</button>}</div></form>
    {ask.isPending && <p className="text-sm text-muted" role="status">Waiting for the complete grounded response…</p>}{ask.data && !cancelled && <Result result={ask.data} />}
  </div>;
}
