"""Verify the compiler's sealed files before consuming a completed package."""

import hashlib
import re
from pathlib import Path


def verify_package_integrity(package_dir):
    root = Path(package_dir).resolve()
    checksum = root / "checksum.sha256"
    if not checksum.is_file():
        raise FileNotFoundError(f"Package checksum manifest missing: {checksum}")
    lines = checksum.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError("Package checksum manifest is empty")
    seen = set()
    for number, line in enumerate(lines, 1):
        match = re.fullmatch(r"([0-9a-fA-F]{64})  ([^\r\n]+)", line)
        if not match:
            raise ValueError(f"Invalid package checksum line {number}")
        expected, relative = match.groups()
        parts = relative.split("/")
        if ("\\" in relative or ":" in relative or relative.startswith("/")
                or any(part in ("", ".", "..") for part in parts)):
            raise ValueError(f"Unsafe package checksum path: {relative}")
        if relative.casefold() in seen:
            raise ValueError(f"Duplicate package checksum path: {relative}")
        seen.add(relative.casefold())
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"Package checksum path escapes root: {relative}")
        if not path.is_file():
            raise FileNotFoundError(f"Sealed package file missing: {relative}")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        if digest.hexdigest() != expected.lower():
            raise ValueError(f"Package checksum mismatch: {relative}")
    return len(lines)
