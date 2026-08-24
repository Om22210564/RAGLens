from contextvars import ContextVar
from uuid import uuid4

trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)


def new_trace_id() -> str:
    return f"tr_{uuid4().hex}"
