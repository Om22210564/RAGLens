from fastapi import APIRouter

from app.core.auth import CurrentPrincipal

router = APIRouter(tags=["identity"])
# APIRouter lets you organize related endpoints into a separate module.
# This creates a router for identity-related routes.

# The tags=["identity"] is mainly useful for FastAPI's automatic API documentation.


@router.get("/me")
async def current_identity(principal: CurrentPrincipal) -> dict[str, object]:
    return {
        "user_id": principal.user_id,
        "tenant_id": principal.tenant_id,
        "roles": sorted(principal.roles),
    }
