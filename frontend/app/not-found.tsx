import Link from "next/link";

export default function NotFound() {
  return <section className="max-w-xl rounded-lg border border-line bg-panel p-5 shadow-panel"><p className="text-sm font-medium text-accent">Not found</p><h1 className="mt-1 text-2xl font-semibold">This route does not exist.</h1><p className="mt-2 text-muted">It may be unavailable, mistyped, or outside the currently supported console features.</p><Link className="mt-4 inline-block rounded bg-accent px-3 py-2 text-sm font-medium text-white hover:bg-accent-strong focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent" href="/">Return to overview</Link></section>;
}
