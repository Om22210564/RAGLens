from fastapi import HTTPException

from app.ingestion.validation import validate_upload


def test_pdf_requires_pdf_signature() -> None:
    try:
        validate_upload("report.pdf", "application/pdf", b"not-a-pdf", 100)
    except HTTPException as exc:
        assert exc.status_code == 415
    else:
        raise AssertionError("Expected invalid PDF to fail")


def test_text_upload_is_hashed() -> None:
    upload = validate_upload("notes.md", "text/markdown", b"# Notes", 100)

    assert upload.filename == "notes.md"
    assert len(upload.content_hash) == 64


def test_path_filename_is_rejected() -> None:
    try:
        validate_upload("../secret.txt", "text/plain", b"hello", 100)
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("Expected unsafe filename to fail")
