from app.ingestion.parsers import parse_document


def test_markdown_parser_preserves_heading_as_section() -> None:
    parsed = parse_document(b"# Overview\n\nFirst paragraph.", "text/markdown", "guide.md")

    assert parsed.blocks[0].text == "First paragraph."
    assert parsed.blocks[0].location.section == "Overview"


def test_html_parser_drops_scripts_and_preserves_heading() -> None:
    parsed = parse_document(
        b"<h1>Security</h1><p>Useful evidence.</p><script>ignore()</script>",
        "text/html",
        "guide.html",
    )

    assert parsed.blocks[0].text == "Useful evidence."
    assert parsed.blocks[0].location.section == "Security"
