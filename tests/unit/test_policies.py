from app.security.policies import PolicyAction, PolicyEngine, RiskLevel


def test_default_policy_allows() -> None:
    decision = PolicyEngine().allow()

    assert decision.action is PolicyAction.ALLOW
    assert decision.risk is RiskLevel.LOW
