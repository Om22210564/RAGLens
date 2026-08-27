import math
from collections.abc import Sequence


def recall_at_k(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 1.0
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def precision_at_k(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    return len(set(retrieved[:k]) & relevant) / k


def hit_rate_at_k(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    return float(bool(set(retrieved[:k]) & relevant))


def reciprocal_rank(retrieved: Sequence[str], relevant: set[str]) -> float:
    for rank, chunk_id in enumerate(retrieved, start=1):
        if chunk_id in relevant:
            return 1 / rank
    return 0.0


def ndcg_at_k(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    dcg = sum(
        1 / math.log2(rank + 1)
        for rank, item in enumerate(retrieved[:k], start=1)
        if item in relevant
    )
    ideal = sum(1 / math.log2(rank + 1) for rank in range(1, min(k, len(relevant)) + 1))
    return dcg / ideal if ideal else 1.0
