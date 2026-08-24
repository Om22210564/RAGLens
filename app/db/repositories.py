from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import Select, select

from app.db.models import Chunk, Document


@dataclass(frozen=True, slots=True)
class AccessScope:
    """Server-derived scope required by every document/chunk query."""

    tenant_id: UUID
    user_id: UUID
    roles: frozenset[str]


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
