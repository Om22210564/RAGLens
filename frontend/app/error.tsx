"use client";

export default function ErrorPage({
  reset,
}: Readonly<{ error: Error & { digest?: string }; reset: () => void }>) {
  return (
    <section className="max-w-xl rounded-lg border border-danger/30 bg-panel p-5">
      <h1 className="text-xl font-semibold">This view could not load</h1>
      <p className="mt-2 text-muted">
        The error is safe to retry. Check the development connection if it
        persists.
      </p>
      <button
        className="mt-4 rounded bg-accent px-3 py-2 text-sm font-medium text-white hover:bg-accent-strong focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        onClick={reset}
      >
        Retry
      </button>
    </section>
  );
}
