from fastapi import APIRouter

from app.core.auth import CurrentPrincipal

router = APIRouter(tags=["identity"])


@router.get("/me")
async def current_identity(principal: CurrentPrincipal) -> dict[str, object]:
    return {
        "user_id": principal.user_id,
        "tenant_id": principal.tenant_id,
        "roles": sorted(principal.roles),
    }
