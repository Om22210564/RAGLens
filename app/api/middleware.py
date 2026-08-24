import time
from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.responses import JSONResponse, Response

from app.core.config import Settings
from app.core.tracing import new_trace_id, trace_id_var


async def trace_and_size_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    settings: Settings = request.app.state.settings
    content_length = request.headers.get("content-length")
    if content_length is not None and int(content_length) > settings.max_request_bytes:
        return JSONResponse(status_code=413, content={"detail": "Request body exceeds size limit"})

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
