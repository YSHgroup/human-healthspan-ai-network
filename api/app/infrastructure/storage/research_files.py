"""Private local storage for bounded researcher document uploads."""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import get_settings

MAX_RESEARCH_FILE_SIZE = 10 * 1024 * 1024
_CHUNK_SIZE = 64 * 1024
_ALLOWED_TYPES = {
    ".csv": "text/csv",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
}


class ResearchFileRejected(ValueError):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class StoredResearchFile:
    key: str
    filename: str
    media_type: str
    size: int
    sha256: str


class ResearchFileStorage:
    def __init__(self, root: Path) -> None:
        self.root = root

    async def store(self, upload: UploadFile) -> StoredResearchFile:
        filename = _safe_filename(upload.filename)
        suffix = Path(filename).suffix.casefold()
        media_type = _ALLOWED_TYPES.get(suffix)
        if media_type is None:
            raise ResearchFileRejected(
                "Only PDF, CSV, and plain-text files are supported",
                status_code=415,
            )
        if upload.size is not None and upload.size > MAX_RESEARCH_FILE_SIZE:
            raise ResearchFileRejected("File exceeds the 10 MiB size limit", status_code=413)

        key = uuid4().hex
        directory = self.root / key[:2]
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        if os.name != "nt":
            os.chmod(self.root, 0o700)
            os.chmod(directory, 0o700)

        temporary = directory / f".{key}.tmp"
        destination = directory / f"{key}.blob"
        digest = hashlib.sha256()
        size = 0
        prefix = bytearray()
        text_decoder = None
        if suffix in {".txt", ".csv"}:
            import codecs

            text_decoder = codecs.getincrementaldecoder("utf-8")("strict")

        try:
            with temporary.open("xb") as target:
                while chunk := await upload.read(_CHUNK_SIZE):
                    size += len(chunk)
                    if size > MAX_RESEARCH_FILE_SIZE:
                        raise ResearchFileRejected(
                            "File exceeds the 10 MiB size limit",
                            status_code=413,
                        )
                    if len(prefix) < 8:
                        prefix.extend(chunk[: 8 - len(prefix)])
                    if text_decoder is not None:
                        try:
                            decoded = text_decoder.decode(chunk)
                        except UnicodeDecodeError as error:
                            raise ResearchFileRejected(
                                "Text and CSV files must use valid UTF-8 encoding"
                            ) from error
                        if "\x00" in decoded:
                            raise ResearchFileRejected("Text and CSV files cannot contain NUL bytes")
                    digest.update(chunk)
                    target.write(chunk)
                if size == 0:
                    raise ResearchFileRejected("Uploaded file cannot be empty")
                if text_decoder is not None:
                    try:
                        text_decoder.decode(b"", final=True)
                    except UnicodeDecodeError as error:
                        raise ResearchFileRejected(
                            "Text and CSV files must use valid UTF-8 encoding"
                        ) from error
                elif not prefix.startswith(b"%PDF-"):
                    raise ResearchFileRejected("The uploaded file is not a valid PDF", status_code=415)
                target.flush()
                os.fsync(target.fileno())
            if os.name != "nt":
                os.chmod(temporary, 0o600)
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)

        return StoredResearchFile(
            key=key,
            filename=filename,
            media_type=media_type,
            size=size,
            sha256=digest.hexdigest(),
        )

    def path_for(self, key: str) -> Path:
        if re.fullmatch(r"[0-9a-f]{32}", key) is None:
            raise ValueError("Invalid research file key")
        return self.root / key[:2] / f"{key}.blob"

    def remove(self, key: str) -> None:
        self.path_for(key).unlink(missing_ok=True)


def get_research_file_storage() -> ResearchFileStorage:
    return ResearchFileStorage(get_settings().research_file_storage_path)


def _safe_filename(filename: str | None) -> str:
    if not filename:
        raise ResearchFileRejected("A file name is required")
    normalized = filename.replace("\\", "/").replace("\r", "").replace("\n", "").replace("\x00", "")
    safe_name = normalized.rsplit("/", 1)[-1].strip()
    if not safe_name or len(safe_name) > 255 or safe_name in {".", ".."}:
        raise ResearchFileRejected("The supplied file name is invalid")
    return safe_name
