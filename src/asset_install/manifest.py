import json
import os
import tempfile
from pathlib import Path
from typing import Any, Optional, List

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
        archive: Optional[str] = None, 
        size: Optional[int] = None, 
        sha256: Optional[str] = None, 
        downloaded_at: Optional[str] = None, 
        source: Optional[str] = None, 
        error: Optional[str] = None,
        outputMode: Optional[str] = None,
        filteredPack: Optional[str] = None,
        filteredCategories: Optional[List[str]] = None,
        filteredTextureSubs: Optional[List[str]] = None,
        temporaryArchiveRemoved: Optional[bool] = None,
        packMetadataGenerated: Optional[bool] = None
    ):
        """Updates the status and metadata of a downloaded version."""
        if version not in self.data["versions"]:
            self.data["versions"][version] = {}

        entry = self.data["versions"][version]
        entry["status"] = status
        
        if outputMode is not None:
            entry["outputMode"] = outputMode
        
        # Original mode keys vs Filtered mode keys
        if "outputMode" in entry:
            if entry["outputMode"] == "original":
                entry["archive"] = archive
                entry["filteredPack"] = None
                entry["temporaryArchiveRemoved"] = False
                if "filteredTextureSubs" in entry:
                    del entry["filteredTextureSubs"]
            elif entry["outputMode"] == "filtered_only":
                entry["archive"] = None
                entry["filteredPack"] = filteredPack
                entry["filteredCategories"] = filteredCategories
                if filteredTextureSubs is not None:
                    entry["filteredTextureSubs"] = filteredTextureSubs
                entry["temporaryArchiveRemoved"] = temporaryArchiveRemoved
                entry["packMetadataGenerated"] = packMetadataGenerated
        else:
            if archive is not None:
                entry["archive"] = archive
                
        if size is not None:
            entry["size"] = size
        if sha256 is not None:
            entry["sha256"] = sha256
        if downloaded_at is not None:
            entry["downloaded_at"] = downloaded_at
        if source is not None:
            entry["source"] = source
            
        if error is not None:
            entry["error"] = error
        elif "error" in entry and status == "complete":
            # Clear error on success
            del entry["error"]
            
        if "warnings" not in entry and entry.get("outputMode") == "filtered_only":
            entry["warnings"] = []
            
        self.save()

    def get_version(self, version: str) -> dict[str, Any]:
        """Returns the dictionary for a version if it exists, else None."""
        return self.data["versions"].get(version)
