import os
from pathlib import Path
from .exceptions import ValidationError

def validate_path(path: str) -> Path:
    try:
        p = Path(path).resolve()
        if not p.exists():
            raise ValidationError(f"Path does not exist: {path}")
        return p
    except OSError as e:
        raise ValidationError(f"Invalid path '{path}': {e}")

def validate_relative_path(path: str):
    p = Path(path)
    if p.is_absolute():
        raise ValidationError(f"Absolute paths not allowed in archive: {path}")
    if '..' in p.parts:
        raise ValidationError(f"Parent directory traversal '..' not allowed: {path}")

def calculate_checksum(file_path: str) -> bytes:
    import hashlib
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.digest()
