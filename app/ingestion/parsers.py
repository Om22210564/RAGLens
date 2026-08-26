import re
from html.parser import HTMLParser
from io import BytesIO

from app.ingestion.types import ParsedBlock, ParsedDocument, SourceLocation


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignored_depth = 0
        self._section: str | None = None
        self.blocks: list[ParsedBlock] = []
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._ignored_depth += 1
        if tag in {"p", "div", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self._flush()

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._ignored_depth:
            self._ignored_depth -= 1
        if tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self._flush(heading=tag.startswith("h"))

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self._buffer.append(data)

    def _flush(self, heading: bool = False) -> None:
        text = " ".join(" ".join(self._buffer).split())
        self._buffer.clear()
        if not text:
            return
        if heading:
            self._section = text
        else:
            self.blocks.append(
                ParsedBlock(text=text, location=SourceLocation(section=self._section))
            )


def _text_blocks(text: str) -> ParsedDocument:
    section: str | None = None
    blocks: list[ParsedBlock] = []
    for raw_block in re.split(r"\n\s*\n", text):
        block = "\n".join(line.rstrip() for line in raw_block.splitlines()).strip()
        if not block:
            continue
        heading_match = re.match(r"^#{1,6}\s+(.+)$", block)
        if heading_match:
            section = heading_match.group(1).strip()
            continue
        blocks.append(ParsedBlock(text=block, location=SourceLocation(section=section)))
    return ParsedDocument(blocks=tuple(blocks))


def parse_document(content: bytes, mime_type: str, filename: str) -> ParsedDocument:
    suffix = filename.rsplit(".", maxsplit=1)[-1].lower()
    if suffix in {"txt", "md"}:
        return _text_blocks(content.decode("utf-8", errors="replace"))
    if suffix in {"html", "htm"}:
        parser = _HTMLTextExtractor()
        parser.feed(content.decode("utf-8", errors="replace"))
        parser._flush()
        return ParsedDocument(blocks=tuple(parser.blocks))
    if suffix == "pdf":
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))
        blocks = tuple(
            ParsedBlock(text=text, location=SourceLocation(page=index + 1))
            for index, page in enumerate(reader.pages)
            if (text := (page.extract_text() or "").strip())
        )
        return ParsedDocument(blocks=blocks)
    raise ValueError(f"No parser for {mime_type}")
