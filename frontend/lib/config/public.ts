import { z } from "zod";

const publicConfigSchema = z.object({ useApiMocks: z.enum(["true", "false"]).default("false").transform((value) => value === "true") });
export const publicConfig = publicConfigSchema.parse({ useApiMocks: process.env.NEXT_PUBLIC_USE_API_MOCKS });
