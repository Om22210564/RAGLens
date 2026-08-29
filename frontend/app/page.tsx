import Link from "next/link";

const tools = [
  {
    href: "/documents",
    title: "Documents",
    text: "Upload a source file and follow its ingestion status.",
  },
  {
    href: "/ask",
    title: "Ask",
    text: "Get a grounded answer with citations and retrieval controls.",
  },
  {
    href: "/traces",
    title: "Traces",
    text: "Open the sanitized summary for a known trace ID.",
  },
  {
    href: "/evaluation",
    title: "Evaluation",
    text: "Inspect a local retrieval-evaluation report.",
  },
];

export default function OverviewPage() {
  return (
    <section className="max-w-4xl space-y-8">
      <div>
        <p className="text-sm font-medium text-accent">
          RAG engineering workspace
        </p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight">
          Build confidence in every grounded answer.
        </h1>
        <p className="mt-3 max-w-2xl text-muted">
          Upload knowledge sources, ask evidence-backed questions, inspect their
          traces, and review offline evaluation metrics from one focused
          workspace.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        {tools.map((tool) => (
          <Link
            key={tool.href}
            href={tool.href}
            className="rounded-lg border border-line bg-panel p-5 shadow-panel transition hover:border-accent hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            <h2 className="font-semibold">{tool.title}</h2>
            <p className="mt-2 text-sm text-muted">{tool.text}</p>
          </Link>
        ))}
      </div>
      <div className="rounded-lg border border-line bg-panel p-5 shadow-panel">
        <h2 className="font-semibold">Development connection</h2>
        <p className="mt-2 text-sm text-muted">
          The workspace uses a same-origin proxy for the local API. Configure
          its origin and development identity in <code>.env.local</code>; these
          settings are not production authentication.
        </p>
      </div>
    </section>
  );
}
