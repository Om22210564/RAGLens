import time
from collections.abc import Awaitable, Callable

# used for type hinting,
# indicating that call_next is a callable that takes a Request and returns an Awaitable[Response].
from fastapi import Request

# Request represents the incoming HTTP request.
from starlette.responses import JSONResponse, Response

from app.core.config import Settings
from app.core.tracing import new_trace_id, trace_id_var
from app.security.rate_limits import InMemoryRateLimiter


async def trace_and_size_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    # A callable that takes a Request and returns an Awaitable that produces a Response.
    # "Continue processing this request and eventually call the appropriate API endpoint."
    settings: Settings = request.app.state.settings
    limiter: InMemoryRateLimiter = request.app.state.rate_limiter
    endpoint_limit = {"/api/v1/documents": 10, "/api/v1/queries": 30}.get(request.url.path)
    if endpoint_limit is not None:
        client_ip = request.client.host if request.client else "unknown"
        user_id = request.headers.get("X-User-Id", "anonymous")
        if not limiter.allowed(f"{request.url.path}:{client_ip}:{user_id}", endpoint_limit):
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            request_size = int(content_length)
        except ValueError:
            return JSONResponse(
                status_code=400, content={"detail": "Invalid Content-Length header"}
            )
        limit = (
            settings.max_upload_bytes
            if request.url.path == "/api/v1/documents"
            else settings.max_request_bytes
        )
        if request_size > limit:
            return JSONResponse(
                status_code=413, content={"detail": "Request body exceeds size limit"}
            )

    trace_id = new_trace_id()
    token = trace_id_var.set(trace_id)
    started = time.perf_counter()
    try:
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        latency_ms = round((time.perf_counter() - started) * 1000)
        response.headers["X-Request-Latency-Ms"] = str(latency_ms)
        return response
    finally:
        trace_id_var.reset(token)


# what call_next is:
# a function that receives a request and asynchronously produces a response.

# Reject requests that are too large, assign each request a unique ID, measure how long it takes,
# expose that information in response headers, and clean up the trace context afterward.
