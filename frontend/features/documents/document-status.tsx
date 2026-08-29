"use client";

import { useQuery } from "@tanstack/react-query";
import { StatusBadge } from "@/components/status-badge";
import { api, type ApiError } from "@/lib/api/client";

const terminalStates = new Set(["ready", "failed", "quarantined"]);
export function DocumentStatus({ documentId }: Readonly<{ documentId: string }>) {
  const status = useQuery({ queryKey: ["document", documentId], queryFn: () => api.document(documentId), refetchInterval: (query) => terminalStates.has(query.state.data?.state ?? "") ? false : 2_000 });
  if (status.isPending) return <p className="text-muted" role="status">Loading document status…</p>;
  if (status.isError) { const error = status.error as unknown as ApiError; return <section><h1 className="text-2xl font-semibold">Document unavailable</h1><p className="mt-3 text-muted">{error.status === 404 ? "This document was not found or is outside your tenant scope." : error.message}</p><button className="mt-4 rounded border border-accent px-3 py-2 text-sm font-medium text-accent" onClick={() => void status.refetch()}>Retry</button></section>; }
  const document = status.data;
  return <section className="max-w-2xl"><p className="text-sm font-medium text-accent">Documents</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">Ingestion status</h1><div className="mt-6 rounded-lg border border-line bg-panel p-5 shadow-panel"><dl className="space-y-4"><div><dt className="text-sm text-muted">Filename</dt><dd className="mt-1 font-medium">{document.filename}</dd></div><div><dt className="text-sm text-muted">State</dt><dd className="mt-1"><StatusBadge value={document.state} /></dd></div><div><dt className="text-sm text-muted">Job status</dt><dd className="mt-1"><StatusBadge value={document.ingestion_status} /></dd></div></dl>{!terminalStates.has(document.state) && <p className="mt-5 text-sm text-muted" role="status">This page checks the individual document status every two seconds.</p>}</div></section>;
}
