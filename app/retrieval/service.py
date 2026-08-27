from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import ColumnElement, func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk, Document, DocumentState
from app.db.repositories import AccessScope
from app.embeddings.providers import EmbeddingProvider, HashEmbeddingProvider
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.types import RetrievalResult, RetrievedChunk


class HybridRetriever:
    def __init__(
        self,
        session: AsyncSession,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self.session = session
        self.embedding_provider = embedding_provider or HashEmbeddingProvider()

    async def search(
        self,
        scope: AccessScope,
        query: str,
        candidate_count: int,
        document_ids: Sequence[UUID] = (),
    ) -> RetrievalResult:
        dense = await self._dense(scope, query, candidate_count, document_ids)
        sparse = await self._sparse(scope, query, candidate_count, document_ids)
        fused = reciprocal_rank_fusion([dense, sparse])
        return RetrievalResult(tuple(dense), tuple(sparse), tuple(fused))

    def _base_conditions(
        self, scope: AccessScope, document_ids: Sequence[UUID]
    ) -> list[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = [
            Chunk.tenant_id == scope.tenant_id,
            Document.tenant_id == scope.tenant_id,
            Document.state == DocumentState.READY.value,
        ]
        if document_ids:
            conditions.append(Chunk.document_id.in_(document_ids))
        return conditions

    def _chunk(self, chunk: Chunk, score: float, source: str) -> RetrievedChunk:
        return RetrievedChunk(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            filename="",  # Populated by the joined document row at query time.
            text=chunk.text,
            page=chunk.page,
            section=chunk.section,
            token_count=chunk.token_count,
            score=score,
            sources=(source,),
        )

    async def _dense(
        self, scope: AccessScope, query: str, limit: int, document_ids: Sequence[UUID]
    ) -> list[RetrievedChunk]:
        embedding = self.embedding_provider.embed_query(query)
        distance = Chunk.embedding.cosine_distance(embedding)
        statement = (
            select(Chunk, Document.filename, (1 - distance).label("score"))
            .join(Document, Document.id == Chunk.document_id)
            .where(*self._base_conditions(scope, document_ids), Chunk.embedding.is_not(None))
            .order_by(distance)
            .limit(limit)
        )
        rows = (await self.session.execute(statement)).all()
        return [
            RetrievedChunk(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                filename=filename,
                text=chunk.text,
                page=chunk.page,
                section=chunk.section,
                token_count=chunk.token_count,
                score=float(score),
                sources=("dense",),
            )
            for chunk, filename, score in rows
        ]

    async def _sparse(
        self, scope: AccessScope, query: str, limit: int, document_ids: Sequence[UUID]
    ) -> list[RetrievedChunk]:
        ts_query = func.plainto_tsquery("simple", query)
        search_vector: ColumnElement[object] = literal_column("chunks.search_vector")
        rank = func.ts_rank_cd(search_vector, ts_query)
        statement = (
            select(Chunk, Document.filename, rank.label("score"))
            .join(Document, Document.id == Chunk.document_id)
            .where(*self._base_conditions(scope, document_ids), search_vector.op("@@")(ts_query))
            .order_by(rank.desc())
            .limit(limit)
        )
        rows = (await self.session.execute(statement)).all()
        return [
            RetrievedChunk(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                filename=filename,
                text=chunk.text,
                page=chunk.page,
                section=chunk.section,
                token_count=chunk.token_count,
                score=float(score),
                sources=("sparse",),
            )
            for chunk, filename, score in rows
        ]
