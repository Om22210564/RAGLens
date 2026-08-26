from pathlib import Path
from uuid import uuid4


class LocalBlobStorage:
    """Development storage adapter; keys are generated server-side and non-guessable."""

    def __init__(self, base_directory: Path) -> None:
        self.base_directory = base_directory

    def save(self, content: bytes) -> str:
        self.base_directory.mkdir(parents=True, exist_ok=True)
        key = f"{uuid4().hex}.source"
        (self.base_directory / key).write_bytes(content)
        return key

    def load(self, key: str) -> bytes:
        path = self.base_directory / key
        if path.name != key:
            raise ValueError("Invalid storage key")
        return path.read_bytes()
