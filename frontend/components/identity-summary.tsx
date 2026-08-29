"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";

export function IdentitySummary() {
  const identity = useQuery({ queryKey: ["me"], queryFn: api.me, retry: false });

  if (identity.isPending) return <span className="text-sm text-muted" aria-live="polite">Verifying development identity…</span>;
  if (identity.isError) return <span className="text-sm font-medium text-danger" aria-live="polite">Development identity unavailable</span>;

  return <div className="text-right text-sm leading-tight"><p className="font-medium">{identity.data.user_id}</p><p className="text-muted">{identity.data.tenant_id} · {identity.data.roles.join(", ")}</p></div>;
}
