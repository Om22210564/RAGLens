from app.embeddings.providers import HashEmbeddingProvider


def test_hash_embedding_is_deterministic_and_normalized() -> None:
    provider = HashEmbeddingProvider(dimensions=8)

    first, second = provider.embed_documents(["hybrid retrieval", "hybrid retrieval"])

    assert first == second
    assert len(first) == 8
    assert round(sum(value * value for value in first), 8) == 1.0
