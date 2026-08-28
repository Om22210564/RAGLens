"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";

export function ConnectionStatus() {
  const health = useQuery({ queryKey: ["health"], queryFn: api.health, retry: 1 });
  const ready = useQuery({ queryKey: ["ready"], queryFn: api.ready, retry: 1 });
  const state = health.isPending || ready.isPending ? "Checking API" : health.isError || ready.isError ? "API unavailable" : "API connected";
  const tone = state === "API connected" ? "text-success" : state === "API unavailable" ? "text-danger" : "text-warning";
  return <span className={`text-sm font-medium ${tone}`} aria-live="polite">{state}</span>;
}
