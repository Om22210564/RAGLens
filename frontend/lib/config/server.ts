import "server-only";

import { z } from "zod";

const serverConfigSchema = z.object({
  RAG_API_ORIGIN: z.string().url().default("http://localhost:8000"),
  RAG_DEV_USER_ID: z.string().min(1).default("user-demo"),
  RAG_DEV_TENANT_ID: z.string().min(1).default("tenant-demo")
});

export const serverConfig = serverConfigSchema.parse({
  RAG_API_ORIGIN: process.env.RAG_API_ORIGIN,
  RAG_DEV_USER_ID: process.env.RAG_DEV_USER_ID,
  RAG_DEV_TENANT_ID: process.env.RAG_DEV_TENANT_ID
});
