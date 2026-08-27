import asyncio

from sqlalchemy import select

from app.core.config import get_settings
from app.db.models import Chunk
from app.db.session import SessionLocal
from app.embeddings.providers import create_embedding_provider


async def reindex() -> None:
    settings = get_settings()
    provider = create_embedding_provider(settings.embedding_provider, settings.embedding_model)
    async with SessionLocal() as session:
        chunks = list(await session.scalars(select(Chunk).order_by(Chunk.id)))
        embeddings = provider.embed_documents([chunk.text for chunk in chunks])
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            chunk.embedding = embedding
        await session.commit()


if __name__ == "__main__":
    asyncio.run(reindex())
