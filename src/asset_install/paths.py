import os
from pathlib import Path

def resolve_path(input_path: str) -> Path:
    """Expands ~ and returns an absolute Path object."""
    return Path(input_path).expanduser().resolve()

def is_path_writable(path: Path) -> bool:
    """Checks if a given path or its closest existing parent is writable."""
    current = path
    while not current.exists():
        if current.parent == current:
            break
        current = current.parent
    return os.access(current, os.W_OK)

def ensure_directory(path: Path) -> None:
    """Creates the directory and its parents if they don't exist."""
    path.mkdir(parents=True, exist_ok=True)
