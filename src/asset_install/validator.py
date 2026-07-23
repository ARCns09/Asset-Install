import hashlib
import zipfile
from pathlib import Path

def calculate_sha256(file_path: Path) -> str:
    """Calculates the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash in chunks of 64K
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def is_valid_zip(file_path: Path) -> bool:
    """Checks if the file at the given path is a valid ZIP archive."""
    if not file_path.exists() or not file_path.is_file():
        return False
    try:
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            # testzip returns the name of the first bad file, or None if all are OK
            return zip_ref.testzip() is None
    except zipfile.BadZipFile:
        return False
    except Exception:
        return False
