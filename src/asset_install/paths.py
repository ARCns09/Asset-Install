import os
import sys
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

def get_app_data_dir() -> Path:
    """Returns the OS-specific application data directory for asset-install."""
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    
    app_dir = base / "asset-install"
    ensure_directory(app_dir)
    return app_dir
