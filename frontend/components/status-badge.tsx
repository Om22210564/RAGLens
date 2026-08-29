const tones: Record<string, string> = { ready: "bg-emerald-50 text-success", queued: "bg-amber-50 text-warning", processing: "bg-amber-50 text-warning", failed: "bg-red-50 text-danger", quarantined: "bg-red-50 text-danger" };

export function StatusBadge({ value }: Readonly<{ value: string }>) {
  const normalized = value.toLowerCase();
  return <span className={`inline-flex rounded px-2 py-1 text-sm font-medium capitalize ${tones[normalized] ?? "bg-slate-100 text-muted"}`}>{value}</span>;
}
