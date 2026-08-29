"use client";

import Link from "next/link";
import { useMutation } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { CopyValueButton } from "@/components/copy-value-button";
import { api, type ApiError } from "@/lib/api/client";

const allowedExtensions = [".txt", ".md", ".html", ".htm", ".pdf"];
const maxUploadBytes = 26_214_400;

function validate(file: File | undefined) {
  if (!file) return "Choose a file to upload.";
  if (!allowedExtensions.some((extension) => file.name.toLowerCase().endsWith(extension))) return "Supported formats are TXT, Markdown, HTML, and PDF.";
  if (file.size === 0) return "The selected file is empty.";
  if (file.size > maxUploadBytes) return "The selected file is larger than the 25 MB upload limit.";
  return undefined;
}

export function DocumentUpload() {
  const input = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File>();
  const [validationError, setValidationError] = useState<string>();
  const upload = useMutation({ mutationFn: api.uploadDocument });
  const apiError = upload.error as ApiError | null;

  function select(nextFile: File | undefined) { setFile(nextFile); setValidationError(validate(nextFile)); upload.reset(); }
  function submit(event: React.FormEvent<HTMLFormElement>) { event.preventDefault(); const error = validate(file); setValidationError(error); if (!error && file) upload.mutate(file); }

  return <div className="max-w-2xl space-y-6"><div><p className="text-sm font-medium text-accent">Documents · F2</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">Upload a document for ingestion.</h1><p className="mt-3 text-muted">Supported types: TXT, Markdown, HTML, and PDF. The backend accepts uploads asynchronously and returns a document ID to inspect.</p></div>
    <form className="rounded-lg border border-line bg-panel p-5 shadow-panel" onSubmit={submit}><label className="block text-sm font-medium" htmlFor="document-file">Document file</label><input ref={input} id="document-file" className="sr-only" type="file" accept=".txt,.md,.html,.htm,.pdf,text/plain,text/markdown,text/html,application/pdf" onChange={(event) => select(event.target.files?.[0])} />
      <button type="button" className="mt-3 flex w-full flex-col items-center rounded-lg border border-dashed border-line px-6 py-10 text-center hover:border-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent" onClick={() => input.current?.click()} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); select(event.dataTransfer.files[0]); }}><span className="font-medium">Drop a file here or choose a file</span><span className="mt-1 text-sm text-muted">Maximum 25 MB</span></button>
      {file && <p className="mt-3 text-sm" aria-live="polite">Selected: <strong>{file.name}</strong> ({Math.ceil(file.size / 1024)} KB)</p>}
      {validationError && <p className="mt-3 text-sm text-danger" role="alert">{validationError}</p>}
      {apiError && <p className="mt-3 text-sm text-danger" role="alert">{apiError.status === 415 ? "Supported formats are TXT, Markdown, HTML, and PDF." : apiError.message}</p>}
      <button className="mt-5 rounded bg-accent px-3 py-2 text-sm font-medium text-white hover:bg-accent-strong disabled:cursor-not-allowed disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent" disabled={!file || Boolean(validationError) || upload.isPending}>{upload.isPending ? "Uploading…" : "Upload document"}</button>
    </form>
    {upload.data && <section className="rounded-lg border border-success/30 bg-panel p-5 shadow-panel" aria-labelledby="upload-accepted"><p className="text-sm font-medium text-success">Upload accepted</p><h2 id="upload-accepted" className="mt-1 text-xl font-semibold">Ingestion is {upload.data.status}.</h2><dl className="mt-4 space-y-3 text-sm"><div><dt className="text-muted">Document ID</dt><dd className="mt-1 flex flex-wrap items-center gap-2 font-mono text-xs"><span>{upload.data.document_id}</span><CopyValueButton value={upload.data.document_id} /></dd></div><div><dt className="text-muted">Ingestion job ID</dt><dd className="mt-1 flex flex-wrap items-center gap-2 font-mono text-xs"><span>{upload.data.ingestion_job_id}</span><CopyValueButton value={upload.data.ingestion_job_id} /></dd></div></dl>{upload.data.duplicate && <p className="mt-3 text-sm text-warning">This upload matches an existing document in your tenant.</p>}<Link className="mt-5 inline-block rounded border border-accent px-3 py-2 text-sm font-medium text-accent hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent" href={`/documents/${upload.data.document_id}`}>Open ingestion status</Link></section>}
  </div>;
}
