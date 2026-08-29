import type { QueryResponse } from "@/lib/api/schemas";

const actionCopy: Record<string, { title: string; detail: string; tone: string }> = {
  allow: { title: "No security action was required", detail: "No non-allow security events were returned with this response.", tone: "border-success/30" },
  warn: { title: "Potentially sensitive content was detected", detail: "Review the returned event categories. The original content is not repeated here.", tone: "border-warning/30" },
  sanitize: { title: "Content was sanitized", detail: "The backend returned a sanitized result. Redacted material is intentionally not available in this console.", tone: "border-warning/30" },
  block: { title: "The request was blocked by policy", detail: "Your draft remains in the composer when it is safe to retain locally. Blocked content is not repeated here.", tone: "border-danger/30" }
};

export function SecuritySummary({ security }: Readonly<{ security: QueryResponse["security"] }>) {
  const copy = actionCopy[security.action] ?? { title: "Security action reported", detail: "Review the returned security event metadata.", tone: "border-line" };
  return <section className={`rounded-lg border ${copy.tone} bg-panel p-5 shadow-panel`} aria-labelledby="security-summary-title"><p className="text-sm font-medium text-muted">Security visibility</p><h3 id="security-summary-title" className="mt-1 font-semibold">{copy.title}</h3><p className="mt-2 text-sm text-muted">{copy.detail}</p>{security.events.length > 0 && <ul className="mt-4 space-y-2 text-sm">{security.events.map((event, index) => <li key={`${event.stage}-${index}`} className="rounded bg-slate-50 p-3"><span className="font-medium capitalize">{event.stage}</span><span className="text-muted"> · {event.risk} risk · {event.action}</span>{event.categories.length > 0 && <p className="mt-1 text-muted">Categories: {event.categories.join(", ")}</p>}</li>)}</ul>}</section>;
}
