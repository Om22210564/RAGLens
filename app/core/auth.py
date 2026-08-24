from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header

from app.core.config import Settings, get_settings
from app.core.errors import AuthenticationRequired


@dataclass(frozen=True, slots=True)
class Principal:
    user_id: str
    tenant_id: str
    roles: frozenset[str] = frozenset({"member"})


async def get_principal(
    settings: Annotated[Settings, Depends(get_settings)],
    user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
    tenant_id: Annotated[str | None, Header(alias="X-Tenant-Id")] = None,
) -> Principal:
    """Development adapter; replace with validated bearer-token auth in production."""
    if not settings.dev_auth_enabled or not user_id or not tenant_id:
        raise AuthenticationRequired()
    return Principal(user_id=user_id, tenant_id=tenant_id)


CurrentPrincipal = Annotated[Principal, Depends(get_principal)]
