"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { TraceInspector } from "@/features/traces/trace-inspector";

export default function TraceDetailPage() {
  const params = useParams<{ traceKey: string }>();
  return <section className="max-w-4xl space-y-6"><div><Link className="text-sm font-medium text-accent hover:underline" href="/traces">← Trace lookup</Link><p className="mt-5 text-sm font-medium text-accent">Trace explorer · F6</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">Trace summary</h1></div><TraceInspector traceId={params.traceKey} initiallyOpen /></section>;
}
