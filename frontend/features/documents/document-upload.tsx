"use client";

import Link from "next/link";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { CopyValueButton } from "@/components/copy-value-button";
import { api, type ApiError } from "@/lib/api/client";

const allowedExtensions = [".txt", ".md", ".html", ".htm", ".pdf"];
const maxUploadBytes = 26_214_400;

function validate(file: File | undefined) {
  if (!file) return "Choose a file to upload.";
  if (
    !allowedExtensions.some((extension) =>
      file.name.toLowerCase().endsWith(extension),
    )
  )
    return "Supported formats are TXT, Markdown, HTML, and PDF.";
  if (file.size === 0) return "The selected file is empty.";
  if (file.size > maxUploadBytes)
    return "The selected file is larger than the 25 MB upload limit.";
  return undefined;
}

export function DocumentUpload() {
  const [file, setFile] = useState<File>();
  const [validationError, setValidationError] = useState<string>();
  const [showUploadInfo, setShowUploadInfo] = useState(false);
  const upload = useMutation({ mutationFn: api.uploadDocument });
  const apiError = upload.error as ApiError | null;

  function select(nextFile: File | undefined) {
    const error = validate(nextFile);
    setFile(nextFile);
    setValidationError(error);
    upload.reset();
    if (!error && nextFile) upload.mutate(nextFile);
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <p className="text-sm font-medium text-accent">Documents</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight">
          Upload a document for ingestion.
        </h1>
        <p className="mt-3 text-muted">
          Supported types: TXT, Markdown, HTML, and PDF. The backend accepts
          uploads asynchronously and returns a document ID to inspect.
        </p>
      </div>
      <section className="form-card">
        <div className="flex items-center gap-2">
          <label className="field-label" htmlFor="document-file">
            Document file
          </label>
          <span className="relative inline-flex">
            <button
              type="button"
              className="flex h-6 w-6 items-center justify-center rounded-full border border-slate-200 bg-slate-50 text-xs font-bold text-muted transition hover:border-accent hover:bg-blue-50 hover:text-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
              aria-label="Upload size information"
              aria-describedby="upload-size-help"
              aria-expanded={showUploadInfo}
              onClick={() => setShowUploadInfo((visible) => !visible)}
              onBlur={() => setShowUploadInfo(false)}
            >
              i
            </button>
            {showUploadInfo && (
              <span
                id="upload-size-help"
                role="tooltip"
                className="absolute bottom-full left-1/2 z-10 mb-2 w-max max-w-48 -translate-x-1/2 rounded-lg bg-ink px-3 py-2 text-center text-xs font-medium text-white shadow-lg"
              >
                Maximum upload size: 25 MB
              </span>
            )}
          </span>
        </div>
        <input
          id="document-file"
          className="field-input mt-4 cursor-pointer file:mr-4 file:rounded-lg file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-accent hover:file:bg-blue-100"
          type="file"
          accept=".txt,.md,.html,.htm,.pdf,text/plain,text/markdown,text/html,application/pdf"
          onChange={(event) => select(event.target.files?.[0])}
        />
        {file && (
          <p className="mt-3 text-sm" aria-live="polite">
            Selected: <strong>{file.name}</strong> (
            {Math.ceil(file.size / 1024)} KB)
          </p>
        )}
        {validationError && (
          <p className="mt-3 text-sm text-danger" role="alert">
            {validationError}
          </p>
        )}
        {apiError && (
          <p className="mt-3 text-sm text-danger" role="alert">
            {apiError.status === 415
              ? "Supported formats are TXT, Markdown, HTML, and PDF."
              : apiError.message}
          </p>
        )}
        {upload.isPending && (
          <p className="mt-4 text-sm font-medium text-accent" role="status">
            Uploading selected document…
          </p>
        )}
      </section>
      {upload.data && (
        <section
          className="rounded-lg border border-success/30 bg-panel p-5 shadow-panel"
          aria-labelledby="upload-accepted"
        >
          <p className="text-sm font-medium text-success">Upload accepted</p>
          <h2 id="upload-accepted" className="mt-1 text-xl font-semibold">
            Ingestion is {upload.data.status}.
          </h2>
          <dl className="mt-4 space-y-3 text-sm">
            <div>
              <dt className="text-muted">Document ID</dt>
              <dd className="mt-1 flex flex-wrap items-center gap-2 font-mono text-xs">
                <span>{upload.data.document_id}</span>
                <CopyValueButton value={upload.data.document_id} />
              </dd>
            </div>
            <div>
              <dt className="text-muted">Ingestion job ID</dt>
              <dd className="mt-1 flex flex-wrap items-center gap-2 font-mono text-xs">
                <span>{upload.data.ingestion_job_id}</span>
                <CopyValueButton value={upload.data.ingestion_job_id} />
              </dd>
            </div>
          </dl>
          {upload.data.duplicate && (
            <p className="mt-3 text-sm text-warning">
              This upload matches an existing document in your tenant.
            </p>
          )}
          <div className="mt-5 flex justify-end">
            <Link
              className="w-full rounded border border-accent px-4 py-2 text-center text-sm font-medium text-accent hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent sm:w-auto"
              href={`/documents/${upload.data.document_id}`}
            >
              Open ingestion status
            </Link>
          </div>
        </section>
      )}
    </div>
  );
}
