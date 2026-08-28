import { NextRequest, NextResponse } from "next/server";
import { serverConfig } from "@/lib/config/server";

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const url = new URL(`/${path.join("/")}`, serverConfig.RAG_API_ORIGIN);
  url.search = request.nextUrl.search;
  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.set("X-User-Id", serverConfig.RAG_DEV_USER_ID);
  headers.set("X-Tenant-Id", serverConfig.RAG_DEV_TENANT_ID);
  const upstream = await fetch(url, { method: request.method, headers, body: request.method === "GET" || request.method === "HEAD" ? undefined : request.body, duplex: "half" });
  const responseHeaders = new Headers(upstream.headers);
  responseHeaders.delete("content-encoding");
  responseHeaders.delete("content-length");
  return new NextResponse(upstream.body, { status: upstream.status, headers: responseHeaders });
}

export const GET = proxy;
export const POST = proxy;
