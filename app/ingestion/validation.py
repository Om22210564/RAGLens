import hashlib
from dataclasses import dataclass
from pathlib import PurePath

from fastapi import HTTPException, status

SUPPORTED_TYPES: dict[str, frozenset[str]] = {
    ".txt": frozenset({"text/plain"}),
    ".md": frozenset({"text/markdown", "text/plain"}),
    ".html": frozenset({"text/html"}),
    ".htm": frozenset({"text/html"}),
    ".pdf": frozenset({"application/pdf"}),
}


@dataclass(frozen=True, slots=True)
class ValidatedUpload:
    filename: str
    mime_type: str
    content_hash: str
    content: bytes


def validate_upload(
    filename: str | None,
    declared_mime_type: str | None,
    content: bytes,
    limit: int,
) -> ValidatedUpload:
    if not filename or PurePath(filename).name != filename:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "A safe filename is required")
    suffix = PurePath(filename).suffix.lower()
    if suffix not in SUPPORTED_TYPES:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported file type")
    if not content:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Uploaded file is empty")
    if len(content) > limit:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Upload exceeds size limit")

    normalized_mime = (declared_mime_type or "").split(";", maxsplit=1)[0].lower()
    if normalized_mime and normalized_mime not in SUPPORTED_TYPES[suffix]:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "File MIME type is not allowed")
    if suffix == ".pdf" and not content.startswith(b"%PDF-"):
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "File content does not match PDF type"
        )

    return ValidatedUpload(
        filename=filename,
        mime_type=normalized_mime or next(iter(SUPPORTED_TYPES[suffix])),
        content_hash=hashlib.sha256(content).hexdigest(),
        content=content,
    )
