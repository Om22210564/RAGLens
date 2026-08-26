from fastapi import APIRouter

router = APIRouter(tags=["health"])
# APIRouter lets you organize related endpoints into a separate module.
# health-related routes are grouped together in this router.


# Is the application alive?
@router.get("/healthz")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


# Is the application ready to serve requests?
@router.get("/readyz")
async def readiness() -> dict[str, str]:
    # Dependency probes are added once Phase 1 starts using the services.
    return {"status": "ready"}
