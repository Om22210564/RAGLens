from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SourceLocation:
    page: int | None = None
    section: str | None = None


@dataclass(frozen=True, slots=True)
class ParsedBlock:
    text: str
    location: SourceLocation = SourceLocation()


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    blocks: tuple[ParsedBlock, ...]
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ChunkDraft:
    text: str
    ordinal: int
    token_count: int
    page: int | None
    section: str | None
