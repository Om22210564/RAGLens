from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz")
async def readiness() -> dict[str, str]:
    # Dependency probes are added once Phase 1 starts using the services.
    return {"status": "ready"}
