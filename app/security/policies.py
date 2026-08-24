from dataclasses import dataclass
from enum import StrEnum


class PolicyAction(StrEnum):
    ALLOW = "allow"
    SANITIZE = "sanitize"
    WARN = "warn"
    BLOCK = "block"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class SecurityDecision:
    risk: RiskLevel
    categories: tuple[str, ...]
    action: PolicyAction
    rule_ids: tuple[str, ...] = ()


class PolicyEngine:
    """Single policy seam; scanner implementations are added in Phase 3."""

    def allow(self) -> SecurityDecision:
        return SecurityDecision(RiskLevel.LOW, (), PolicyAction.ALLOW)
