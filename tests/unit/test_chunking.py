from app.ingestion.chunking import chunk_document
from app.ingestion.types import ParsedBlock, ParsedDocument, SourceLocation


def test_chunking_preserves_section_and_overlap() -> None:
    parsed = ParsedDocument(
        blocks=(
            ParsedBlock(
                text="one two three four five six seven",
                location=SourceLocation(page=2, section="Intro"),
            ),
        )
    )

    chunks = chunk_document(parsed, target_tokens=4, overlap_tokens=1)

    assert [chunk.text for chunk in chunks] == ["one two three four", "four five six seven"]
    assert all(chunk.page == 2 and chunk.section == "Intro" for chunk in chunks)


def test_chunking_rejects_invalid_overlap() -> None:
    parsed = ParsedDocument(blocks=())

    try:
        chunk_document(parsed, target_tokens=4, overlap_tokens=4)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("Expected invalid overlap to fail")
