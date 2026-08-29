import { z } from "zod";
import { documentStatusSchema, healthSchema, identitySchema, ingestionAcceptedSchema } from "@/lib/api/schemas";
import { publicConfig } from "@/lib/config/public";

export type ApiError = { status: number; message: string; traceId?: string; retryable: boolean; fieldErrors?: Record<string, string> };
const mockIdentity = { user_id: "user-demo", tenant_id: "tenant-demo", roles: ["member"] };

export function normalizeApiError(response: Response, body: unknown): ApiError {
  const detail = typeof body === "object" && body !== null && "detail" in body ? (body as { detail: unknown }).detail : undefined;
  const fieldErrors = Array.isArray(detail) ? Object.fromEntries(detail.map((item) => {
    const issue = item as { loc?: unknown[]; msg?: string };
    return [issue.loc?.slice(1).join(".") || "form", issue.msg || "Invalid value"];
  })) : undefined;
  return { status: response.status, message: typeof detail === "string" ? detail : response.statusText || "Request failed", traceId: response.headers.get("X-Trace-Id") || undefined, retryable: response.status === 429 || response.status >= 500, fieldErrors };
}

async function request<T>(path: string, schema: z.ZodType<T>, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/backend${path}`, init);
  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) throw normalizeApiError(response, body);
  return schema.parse(body);
}

export const api = {
  health: () => publicConfig.useApiMocks ? Promise.resolve({ status: "ok" }) : request("/healthz", healthSchema),
  ready: () => publicConfig.useApiMocks ? Promise.resolve({ status: "ready" }) : request("/readyz", healthSchema),
  me: () => publicConfig.useApiMocks ? Promise.resolve(mockIdentity) : request("/api/v1/me", identitySchema),
  uploadDocument: (file: File) => publicConfig.useApiMocks
    ? Promise.resolve({ document_id: "00000000-0000-4000-8000-000000000001", ingestion_job_id: "00000000-0000-4000-8000-000000000002", status: "queued", duplicate: false })
    : request("/api/v1/documents", ingestionAcceptedSchema, { method: "POST", body: (() => { const form = new FormData(); form.append("file", file); return form; })() }),
  document: (documentId: string) => publicConfig.useApiMocks
    ? Promise.resolve({ id: documentId, filename: "example.md", mime_type: "text/markdown", state: "ready", ingestion_job_id: "00000000-0000-4000-8000-000000000002", ingestion_status: "ready" })
    : request(`/api/v1/documents/${encodeURIComponent(documentId)}`, documentStatusSchema)
};
