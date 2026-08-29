"use client";

import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { type FormEvent, useEffect, useRef, useState } from "react";
import { z } from "zod";
import { CopyValueButton } from "@/components/copy-value-button";
import { SecuritySummary } from "@/components/security-summary";
import { TraceInspector } from "@/features/traces/trace-inspector";
import { api, type ApiError } from "@/lib/api/client";
import { queryRequestSchema, type QueryResponse } from "@/lib/api/schemas";

const uuidSchema = z.string().uuid();
const presetSchema = z.object({ name: z.string().min(1).max(60), topK: z.number().int().min(1).max(20), documentIds: z.string(), transform: z.boolean(), rerank: z.boolean() });
type RetrievalPreset = z.infer<typeof presetSchema>;
const presetStorageKey = "rag-console.retrieval-presets";

function Result({ result }: Readonly<{ result: QueryResponse }>) {
  return <section className="space-y-4" aria-live="polite"><div className="rounded-lg border border-line bg-panel p-5 shadow-panel"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-sm font-medium text-accent">Grounded response</p><h2 className="mt-1 text-xl font-semibold">{result.answerability.status === "answerable" ? "Answer supported by retrieved evidence" : "Evidence may be insufficient"}</h2></div><span className="rounded bg-slate-100 px-2 py-1 text-sm">Confidence {Math.round(result.answerability.confidence * 100)}%</span></div><p className="mt-4 whitespace-pre-wrap leading-7">{result.answer}</p></div>
    <div className="grid gap-4 md:grid-cols-2"><section className="rounded-lg border border-line bg-panel p-5 shadow-panel"><h3 className="font-semibold">Citations</h3>{result.citations.length === 0 ? <p className="mt-2 text-sm text-muted">No citations were returned.</p> : <ol className="mt-3 space-y-3">{result.citations.map((citation) => <li key={citation.id} className="text-sm"><p className="font-medium">[{citation.id}] {citation.filename}</p><p className="mt-1 text-muted">{citation.section ?? "No section"}{citation.page !== null ? ` · page ${citation.page}` : ""}</p><p className="mt-1 break-all font-mono text-xs text-muted">{citation.document_id}</p></li>)}</ol>}</section>
      <section className="rounded-lg border border-line bg-panel p-5 shadow-panel"><h3 className="font-semibold">Response details</h3><dl className="mt-3 space-y-2 text-sm"><div className="flex justify-between gap-4"><dt className="text-muted">Context chunks</dt><dd>{result.usage.context_chunks}</dd></div><div className="flex justify-between gap-4"><dt className="text-muted">Dense candidates</dt><dd>{result.usage.dense_candidates}</dd></div><div className="flex justify-between gap-4"><dt className="text-muted">Sparse candidates</dt><dd>{result.usage.sparse_candidates}</dd></div></dl><div className="mt-4"><p className="text-sm text-muted">Trace ID</p><div className="mt-1 flex flex-wrap gap-2"><Link className="break-all font-mono text-xs text-accent hover:underline" href={`/traces/${encodeURIComponent(result.trace_id)}`}>{result.trace_id}</Link><CopyValueButton value={result.trace_id} /></div></div></section></div>
    <SecuritySummary security={result.security} />
    <TraceInspector traceId={result.trace_id} />
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
  const [presetName, setPresetName] = useState("");
  const [presets, setPresets] = useState<RetrievalPreset[]>([]);
  const [presetsLoaded, setPresetsLoaded] = useState(false);
  const [formError, setFormError] = useState<string>();
  const [cancelled, setCancelled] = useState(false);
  const ask = useMutation({ mutationFn: ({ payload, signal }: { payload: z.infer<typeof queryRequestSchema>; signal: AbortSignal }) => api.ask(payload, signal) });
  const apiError = ask.error as unknown as ApiError | null;

  useEffect(() => {
    try { const parsed = z.array(presetSchema).safeParse(JSON.parse(window.localStorage.getItem(presetStorageKey) ?? "[]")); if (parsed.success) setPresets(parsed.data); } catch { /* Ignore malformed local-only saved presets. */ }
    setPresetsLoaded(true);
  }, []);

  function savePreset() {
    const parsed = presetSchema.safeParse({ name: presetName.trim(), topK, documentIds, transform, rerank });
    if (!parsed.success) { setFormError("Give this local preset a name and use a retrieval count from 1 to 20."); return; }
    const next = [...presets.filter((preset) => preset.name !== parsed.data.name), parsed.data];
    window.localStorage.setItem(presetStorageKey, JSON.stringify(next)); setPresets(next); setPresetName(""); setFormError(undefined);
  }
  function applyPreset(name: string) { const preset = presets.find((candidate) => candidate.name === name); if (!preset) return; setTopK(preset.topK); setDocumentIds(preset.documentIds); setTransform(preset.transform); setRerank(preset.rerank); setFormError(undefined); }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const ids = documentIds.split(/[\s,]+/).filter(Boolean);
    if (ids.some((id) => !uuidSchema.safeParse(id).success)) { setFormError("Each document filter must be a valid UUID."); return; }
    const parsed = queryRequestSchema.safeParse({ query: query.trim(), top_k: topK, document_ids: ids, transform, rerank });
    if (!parsed.success) { setFormError("Enter a question and choose a retrieval count from 1 to 20."); return; }
    controller.current = new AbortController(); setCancelled(false); setFormError(undefined); ask.mutate({ payload: parsed.data, signal: controller.current.signal });
  }
  function cancel() { controller.current?.abort(); setCancelled(true); }

  return <div className="max-w-4xl space-y-6"><div><p className="text-sm font-medium text-accent">Grounded answers</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">Ask a grounded question.</h1><p className="mt-3 text-muted">This sends one buffered request and returns the completed answer with its citations. It does not provide message streaming or conversation history.</p></div>
    <form className="form-card" onSubmit={submit}><div className="grid grid-cols-[8rem_minmax(0,1fr)] items-start gap-6"><label className="field-label pt-3" htmlFor="query">Question</label><textarea id="query" value={query} onChange={(event) => setQuery(event.target.value)} className="field-textarea min-h-[220px] rounded-2xl px-5 py-4" placeholder="Ask about documents available to your tenant." required disabled={ask.isPending} /></div>
      <fieldset className="mt-6 rounded-xl border border-slate-100 bg-slate-50/70 p-4"><legend className="px-1 text-sm font-semibold">Retrieval controls</legend><p className="mt-1 text-sm text-muted">These options use the backend’s supported retrieval contract. Strategy selection and candidate scores are not available.</p><div className="mt-4 grid gap-4 sm:grid-cols-2"><label className="text-sm font-semibold text-slate-700">Retrieval count <input className="field-input mt-1" type="number" min="1" max="20" value={topK} onChange={(event) => setTopK(Number(event.target.value))} disabled={ask.isPending} /><span className="mt-1 block text-xs font-normal text-muted">1–20 chunks; default 8.</span></label><label className="text-sm font-semibold text-slate-700">Document ID filters <input className="field-input mt-1" value={documentIds} onChange={(event) => setDocumentIds(event.target.value)} placeholder="UUIDs, comma-separated" disabled={ask.isPending} /><span className="mt-1 block text-xs font-normal text-muted">Optional. Limits search to IDs you already know.</span></label></div><div className="mt-4 flex flex-wrap gap-5"><label className="flex items-center gap-2 text-sm font-medium"><input type="checkbox" checked={transform} onChange={(event) => setTransform(event.target.checked)} disabled={ask.isPending} /> Transform query <span className="font-normal text-muted">(decompose retrieval wording)</span></label><label className="flex items-center gap-2 text-sm font-medium"><input type="checkbox" checked={rerank} onChange={(event) => setRerank(event.target.checked)} disabled={ask.isPending} /> Rerank results <span className="font-normal text-muted">(local baseline)</span></label></div></fieldset>
      <div className="mt-5 border-t border-line pt-5"><label className="field-label" htmlFor="retrieval-preset">Local retrieval preset</label><p className="mt-1 text-sm text-muted">Saved only in this browser. Presets are not shared with the backend.</p><div className="mt-3 grid gap-3 sm:grid-cols-2"><select id="retrieval-preset" className="field-input min-w-0" defaultValue="" onChange={(event) => applyPreset(event.target.value)} disabled={!presetsLoaded || ask.isPending}><option value="">Apply saved preset…</option>{presets.map((preset) => <option key={preset.name} value={preset.name}>{preset.name}</option>)}</select><input className="field-input min-w-0" value={presetName} maxLength={60} onChange={(event) => setPresetName(event.target.value)} placeholder="Preset name" disabled={ask.isPending} /></div><div className="mt-3 flex justify-end"><button className="inline-flex w-full items-center justify-center rounded border border-accent px-5 py-2.5 text-sm font-medium text-accent transition hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto" type="button" disabled={ask.isPending} onClick={savePreset}>Save locally</button></div></div>
      {formError && <p className="mt-3 text-sm text-danger" role="alert">{formError}</p>}{ask.isError && !cancelled && <p className="mt-3 text-sm text-danger" role="alert">{apiError?.status === 403 ? "This request was blocked by policy. Your draft remains in the composer, but its content is not repeated here." : apiError?.message === "Backend API is unavailable" ? "The API is not running or cannot be reached. Start the local backend and try again." : apiError?.status === 503 ? "The generation provider is unavailable. You can retry later." : apiError?.message ?? "The query could not be completed."}</p>}{cancelled && <p className="mt-3 text-sm text-muted" role="status">Request cancelled locally.</p>}
      <div className="mt-6 flex flex-col-reverse gap-3 border-t border-line pt-5 sm:flex-row sm:justify-end"><button className="inline-flex w-full items-center justify-center rounded-xl border-2 border-accent bg-blue-50 px-8 py-4 text-base font-semibold text-accent shadow-sm transition hover:-translate-y-px hover:bg-blue-100 hover:shadow-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0 sm:w-auto" disabled={ask.isPending}>{ask.isPending ? "Generating…" : "Ask question"}</button>{ask.isPending && <button className="secondary-action w-full sm:w-auto" type="button" onClick={cancel}>Cancel</button>}</div></form>
    {ask.isPending && <p className="text-sm text-muted" role="status">Waiting for the complete grounded response…</p>}{ask.data && !cancelled && <Result result={ask.data} />}
  </div>;
}
