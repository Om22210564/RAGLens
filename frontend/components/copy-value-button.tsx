"use client";

import { useState } from "react";

export function CopyValueButton({ value, label = "Copy" }: Readonly<{ value: string; label?: string }>) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2_000);
  }
  return <button type="button" className="rounded border border-line px-2 py-1 text-xs font-medium hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent" onClick={() => void copy()}>{copied ? "Copied" : label}<span className="sr-only" aria-live="polite">{copied ? " value copied" : ""}</span></button>;
}
