FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev --no-install-project
COPY . .
RUN uv sync --frozen --no-dev
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
