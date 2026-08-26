from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import Principal
from app.db.models import Chunk, Document, Tenant, TenantMembership, User


@dataclass(frozen=True, slots=True)
class AccessScope:
    """Server-derived scope required by every document/chunk query."""

    tenant_id: UUID
    user_id: UUID
    roles: frozenset[str]


async def resolve_development_scope(session: AsyncSession, principal: Principal) -> AccessScope:
    """Provision deterministic local identities only for the development adapter.

    A production authentication adapter must instead verify an existing identity
    and membership before constructing an AccessScope.
    """
    tenant = await session.scalar(select(Tenant).where(Tenant.name == principal.tenant_id))
    if tenant is None:
        tenant = Tenant(name=principal.tenant_id)
        session.add(tenant)
        await session.flush()

    user = await session.scalar(select(User).where(User.external_subject == principal.user_id))
    if user is None:
        user = User(external_subject=principal.user_id)
        session.add(user)
        await session.flush()

    membership = await session.scalar(
        select(TenantMembership).where(
            TenantMembership.tenant_id == tenant.id,
            TenantMembership.user_id == user.id,
        )
    )
    if membership is None:
        membership = TenantMembership(tenant_id=tenant.id, user_id=user.id, role="member")
        session.add(membership)
        await session.flush()

    return AccessScope(tenant_id=tenant.id, user_id=user.id, roles=frozenset({membership.role}))


class DocumentRepository:
    def visible_documents(self, scope: AccessScope) -> Select[tuple[Document]]:
        return select(Document).where(Document.tenant_id == scope.tenant_id)

    def by_id(self, scope: AccessScope, document_id: UUID) -> Select[tuple[Document]]:
        return self.visible_documents(scope).where(Document.id == document_id)


class ChunkRepository:
    def visible_chunks(self, scope: AccessScope) -> Select[tuple[Chunk]]:
        return select(Chunk).where(Chunk.tenant_id == scope.tenant_id)

    def for_document(self, scope: AccessScope, document_id: UUID) -> Select[tuple[Chunk]]:
        return self.visible_chunks(scope).where(Chunk.document_id == document_id)
