import json
import os
import tempfile
from pathlib import Path
from typing import Any

MANIFEST_FILENAME = "manifest.json"

class Manifest:
    def __init__(self, download_directory: Path):
        self.download_directory = download_directory
        self.manifest_path = self.download_directory / MANIFEST_FILENAME
        self.data: dict[str, Any] = {
            "repository": "InventivetalentDev/minecraft-assets",
            "downloadDirectory": str(self.download_directory.resolve()),
            "versions": {}
        }
        self.load()

    def load(self):
        """Loads existing manifest data if the file exists."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    # Merge existing versions
                    if "versions" in loaded_data:
                        self.data["versions"].update(loaded_data["versions"])
            except json.JSONDecodeError:
                # If the manifest is corrupted, we overwrite it.
                pass

    def save(self):
        """Saves the manifest atomically."""
        if not self.download_directory.exists():
            return

        temp_fd, temp_path = tempfile.mkstemp(
            dir=self.download_directory, prefix="manifest.json.tmp", text=True
        )
        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            
            # Atomic rename (replace existing on POSIX and Windows)
            os.replace(temp_path, self.manifest_path)
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def update_version(
        self,
        version: str,
        status: str,
        source: str = None,
        archive: str = None,
        size: int = None,
        sha256: str = None,
        downloaded_at: str = None,
        error: str = None
    ):
        """Updates the status and details of a specific version."""
        if version not in self.data["versions"]:
            self.data["versions"][version] = {}
        
        v_data = self.data["versions"][version]
        
        v_data["status"] = status
        
        if source is not None:
            v_data["source"] = source
        if archive is not None:
            v_data["archive"] = archive
        if size is not None:
            v_data["size"] = size
        if sha256 is not None:
            v_data["sha256"] = sha256
        if downloaded_at is not None:
            v_data["downloadedAt"] = downloaded_at
        
        # Always set error, can be null
        v_data["error"] = error

        self.save()

    def get_version(self, version: str) -> dict[str, Any]:
        """Returns the dictionary for a version if it exists, else None."""
        return self.data["versions"].get(version)
