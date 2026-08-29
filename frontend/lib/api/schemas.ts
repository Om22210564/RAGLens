import { z } from "zod";

export const healthSchema = z.object({ status: z.string() });
export const identitySchema = z.object({ user_id: z.string(), tenant_id: z.string(), roles: z.array(z.string()) });
export const ingestionAcceptedSchema = z.object({ document_id: z.string().uuid(), ingestion_job_id: z.string().uuid(), status: z.string(), duplicate: z.boolean() });
export const documentStatusSchema = z.object({ id: z.string().uuid(), filename: z.string(), mime_type: z.string(), state: z.string(), ingestion_job_id: z.string().uuid(), ingestion_status: z.string() });
export const queryRequestSchema = z.object({ query: z.string().min(1), top_k: z.number().int().min(1).max(20).default(8), document_ids: z.array(z.string().uuid()).default([]), transform: z.boolean().default(false), rerank: z.boolean().default(false) });
export const queryResponseSchema = z.object({
  trace_id: z.string(), answer: z.string(), answerability: z.object({ status: z.string(), confidence: z.number() }).passthrough(),
  citations: z.array(z.object({ id: z.number().int(), document_id: z.string().uuid(), chunk_id: z.string().uuid(), filename: z.string(), page: z.number().int().nullable(), section: z.string().nullable() })),
  usage: z.object({ dense_candidates: z.number().int(), sparse_candidates: z.number().int(), context_chunks: z.number().int() }), security: z.object({ action: z.string(), events: z.array(z.unknown()) }).passthrough(), rewritten_queries: z.array(z.string())
});
export const traceResponseSchema = z.object({ trace_id: z.string(), outcome: z.string(), latency_ms: z.number(), retrieval_events: z.array(z.object({ stage: z.string(), output_count: z.number(), latency_ms: z.number() })), security_events: z.array(z.object({ stage: z.string(), risk: z.string(), action: z.string(), categories: z.array(z.string()) })) });

export type Identity = z.infer<typeof identitySchema>;
export type QueryRequest = z.infer<typeof queryRequestSchema>;
export type QueryResponse = z.infer<typeof queryResponseSchema>;
