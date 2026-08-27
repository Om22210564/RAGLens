from app.evaluation.metrics import (
    hit_rate_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_retrieval_metrics() -> None:
    retrieved = ["wrong", "relevant-a", "relevant-b"]
    relevant = {"relevant-a", "relevant-b"}

    assert recall_at_k(retrieved, relevant, 2) == 0.5
    assert precision_at_k(retrieved, relevant, 2) == 0.5
    assert hit_rate_at_k(retrieved, relevant, 2) == 1.0
    assert reciprocal_rank(retrieved, relevant) == 0.5
    assert ndcg_at_k(retrieved, relevant, 2) > 0
