from contextvars import ContextVar
from uuid import uuid4

trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)

# A unique trace ID is generated for each request and stored in a context variable.
# It follows asynchronous work, so logs can be searched for one complete request.


def new_trace_id() -> str:
    return f"tr_{uuid4().hex}"
