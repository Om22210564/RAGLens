import re

from app.ingestion.types import ChunkDraft, ParsedDocument


def estimate_tokens(text: str) -> int:
    return len(re.findall(r"\S+", text))


def chunk_document(
    parsed: ParsedDocument, target_tokens: int, overlap_tokens: int
) -> list[ChunkDraft]:
    if target_tokens <= 0 or overlap_tokens < 0 or overlap_tokens >= target_tokens:
        raise ValueError("Chunk target must be positive and overlap smaller than target")

    chunks: list[ChunkDraft] = []
    for block in parsed.blocks:
        words = re.findall(r"\S+", block.text)
        start = 0
        while start < len(words):
            end = min(start + target_tokens, len(words))
            text = " ".join(words[start:end])
            chunks.append(
                ChunkDraft(
                    text=text,
                    ordinal=len(chunks),
                    token_count=end - start,
                    page=block.location.page,
                    section=block.location.section,
                )
            )
            if end == len(words):
                break
            start = end - overlap_tokens
    return chunks
