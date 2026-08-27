from dataclasses import replace

from app.retrieval.types import RetrievedChunk
from app.security.policies import (
    DeterministicSecurityScanner,
    PolicyAction,
    ScanResult,
    SecurityStage,
)


def filter_untrusted_context(
    chunks: list[RetrievedChunk], scanner: DeterministicSecurityScanner
) -> tuple[list[RetrievedChunk], list[ScanResult]]:
    safe_chunks: list[RetrievedChunk] = []
    events: list[ScanResult] = []
    for chunk in chunks:
        result = scanner.scan(chunk.text, SecurityStage.CONTEXT)
        if result.decision.action is PolicyAction.BLOCK:
            events.append(result)
            continue
        if result.decision.action is PolicyAction.SANITIZE:
            events.append(result)
            safe_chunks.append(replace(chunk, text=result.sanitized_text))
            continue
        safe_chunks.append(chunk)
    return safe_chunks, events
