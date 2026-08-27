from app.query.transforms import QueryRouter


def test_router_decomposes_comparison_when_enabled() -> None:
    plan = QueryRouter().plan("Compare dense retrieval and BM25", enabled=True)

    assert plan.transformed
    assert plan.reason == "comparison_decomposition"
    assert len(plan.queries) == 4


def test_router_leaves_simple_question_unchanged() -> None:
    plan = QueryRouter().plan("What is RRF?", enabled=True)

    assert plan.queries == ("What is RRF?",)
    assert not plan.transformed
