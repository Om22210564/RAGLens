import re
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


class SecurityStage(StrEnum):
    INPUT = "input"
    CONTEXT = "context"
    OUTPUT = "output"


@dataclass(frozen=True, slots=True)
class SecurityDecision:
    risk: RiskLevel
    categories: tuple[str, ...]
    action: PolicyAction
    rule_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ScanResult:
    decision: SecurityDecision
    sanitized_text: str


class DeterministicSecurityScanner:
    """Pattern and heuristic baseline; classifier adapters may add evidence later."""

    _injection_patterns = (
        (
            "PI-001",
            "prompt_injection",
            re.compile(r"\bignore (all |any |the )?(previous|prior) instructions?\b", re.I),
        ),
        (
            "PI-002",
            "system_prompt_extraction",
            re.compile(r"\b(reveal|show|repeat).{0,40}\b(system|developer) prompt\b", re.I),
        ),
        (
            "PI-003",
            "instruction_override",
            re.compile(r"\bpretend.{0,40}\b(developer|system)\b", re.I),
        ),
        (
            "PI-004",
            "tool_instruction",
            re.compile(r"\b(execute|run|call) (this )?(command|tool)\b", re.I),
        ),
    )
    _secret_patterns = (
        ("SEC-001", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
        ("SEC-002", re.compile(r"\bgsk_[A-Za-z0-9_-]{16,}\b")),
        ("SEC-003", re.compile(r"\b(?:bearer\s+)?[A-Za-z0-9_-]{32,}\b", re.I)),
        ("SEC-004", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
        (
            "SEC-005",
            re.compile(
                r"\b(?:password|api\s*[_-]?\s*key|secret)\s*(?:is|:|=)\s*\S+",
                re.I,
            ),
        ),
    )

    def scan(self, text: str, stage: SecurityStage) -> ScanResult:
        categories: list[str] = []
        rule_ids: list[str] = []
        for rule_id, category, pattern in self._injection_patterns:
            if pattern.search(text):
                categories.append(category)
                rule_ids.append(rule_id)

        sanitized = text
        secret_found = False
        for rule_id, pattern in self._secret_patterns:
            if pattern.search(sanitized):
                secret_found = True
                rule_ids.append(rule_id)
                sanitized = pattern.sub("[REDACTED_SECRET]", sanitized)
        if secret_found:
            categories.append("sensitive_information")

        if any(category != "sensitive_information" for category in categories):
            return ScanResult(
                SecurityDecision(
                    RiskLevel.HIGH, tuple(categories), PolicyAction.BLOCK, tuple(rule_ids)
                ),
                sanitized,
            )
        if secret_found:
            action = (
                PolicyAction.SANITIZE
                if stage in {SecurityStage.CONTEXT, SecurityStage.OUTPUT}
                else PolicyAction.WARN
            )
            return ScanResult(
                SecurityDecision(RiskLevel.MEDIUM, tuple(categories), action, tuple(rule_ids)),
                sanitized,
            )
        return ScanResult(SecurityDecision(RiskLevel.LOW, (), PolicyAction.ALLOW), text)


class PolicyEngine:
    """Compatibility seam for future tenant-specific policy configuration."""

    def allow(self) -> SecurityDecision:
        return SecurityDecision(RiskLevel.LOW, (), PolicyAction.ALLOW)
