from uuid import uuid4

from app.db.models import Chunk, Document
from app.db.repositories import AccessScope, ChunkRepository, DocumentRepository


def test_document_repository_always_scopes_to_tenant() -> None:
    tenant_id = uuid4()
    scope = AccessScope(tenant_id=tenant_id, user_id=uuid4(), roles=frozenset({"member"}))

    statement = DocumentRepository().visible_documents(scope)

    assert "documents.tenant_id" in str(statement)
    assert str(tenant_id) not in str(statement)  # Bound parameter, never interpolated SQL.


def test_chunk_repository_scopes_document_query_to_tenant() -> None:
    tenant_id = uuid4()
    scope = AccessScope(tenant_id=tenant_id, user_id=uuid4(), roles=frozenset({"member"}))

    statement = ChunkRepository().for_document(scope, uuid4())

    assert "chunks.tenant_id" in str(statement)
    assert "chunks.document_id" in str(statement)
    assert Document.__tablename__ == "documents"
    assert Chunk.__tablename__ == "chunks"
