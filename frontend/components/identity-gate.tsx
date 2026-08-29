"use client";

import { useQuery } from "@tanstack/react-query";
import { api, type ApiError } from "@/lib/api/client";

function messageFor(error: unknown) {
  const apiError = error as Partial<ApiError>;
  if (apiError.status === 401) return "The backend rejected the development identity. Check RAG_DEV_USER_ID and RAG_DEV_TENANT_ID in .env.local.";
  return "The frontend could not establish a development connection. Start the API, then verify RAG_API_ORIGIN in .env.local.";
}

export function IdentityGate({ children }: Readonly<{ children: React.ReactNode }>) {
  const identity = useQuery({ queryKey: ["me"], queryFn: api.me, retry: false });
  if (identity.isPending) return <p className="text-muted" role="status">Establishing development connection…</p>;
  if (identity.isError) return <section className="max-w-xl rounded-lg border border-danger/30 bg-panel p-5 shadow-panel" aria-labelledby="connection-title"><p className="text-sm font-medium text-danger">Development connection</p><h1 id="connection-title" className="mt-1 text-xl font-semibold">Identity verification failed</h1><p className="mt-2 text-muted">{messageFor(identity.error)}</p><button className="mt-4 rounded bg-accent px-3 py-2 text-sm font-medium text-white hover:bg-accent-strong focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent" onClick={() => void identity.refetch()}>Retry connection</button></section>;
  return <>{children}</>;
}
