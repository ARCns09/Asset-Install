import os
from pathlib import Path

def get_versions_file_path() -> Path:
    """Returns the path to the config/versions.txt file."""
    # Assuming config is at the root of the project (parent of src)
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "config" / "versions.txt"
    return config_path

def get_approved_versions() -> list[str]:
    """Loads and returns the list of approved versions from the config file."""
    versions_path = get_versions_file_path()
    if not versions_path.exists():
        raise FileNotFoundError(f"Missing versions file at {versions_path}")
    
    versions = []
    with open(versions_path, "r", encoding="utf-8") as f:
        for line in f:
            version = line.strip()
            if version:
                versions.append(version)
    return versions
