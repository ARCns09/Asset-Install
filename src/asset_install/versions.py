import json
import re
import requests
import datetime
from pathlib import Path
from typing import List, Dict
import importlib.resources

from .paths import get_app_data_dir

# Match 1.x.y or 26.x.y
VERSION_REGEX = re.compile(r"^(1|[2-9]\d+)\.\d+(?:\.\d+)?$")

def get_fallback_versions_path() -> Path:
    """Returns the path to the bundled versions.txt file."""
    return importlib.resources.files("asset_install").joinpath("versions.txt")

def get_cached_versions_path() -> Path:
    """Returns the path to the local versions cache."""
    return get_app_data_dir() / "versions.json"

def is_valid_version(version: str) -> bool:
    """Checks if a version string is a valid Minecraft release."""
    return bool(VERSION_REGEX.match(version))

def parse_version_tuple(version: str) -> tuple:
    """Parses a version string into a tuple of integers for numerical sorting."""
    return tuple(map(int, version.split('.')))

def sort_versions(versions: List[str]) -> List[str]:
    """Sorts a list of versions numerically."""
    return sorted(versions, key=parse_version_tuple)

def group_versions(versions: List[str]) -> Dict[str, List[str]]:
    """Groups a sorted list of versions into families (e.g. 1.21.x)."""
    groups = {}
    for v in versions:
        parts = v.split('.')
        family = f"{parts[0]}.{parts[1]}.x"
        if family not in groups:
            groups[family] = []
        groups[family].append(v)
    return groups

def load_bundled_versions() -> List[str]:
    """Loads the bundled list of approved versions from config/versions.txt."""
    versions_path = get_fallback_versions_path()
    if not versions_path.exists():
        return []
    
    versions = []
    with open(versions_path, "r", encoding="utf-8") as f:
        for line in f:
            v = line.strip()
            if v and is_valid_version(v):
                versions.append(v)
    return sort_versions(versions)

def fetch_versions_from_github() -> List[str]:
    """Fetches branches from GitHub API and extracts valid versions."""
    url = "https://api.github.com/repos/InventivetalentDev/minecraft-assets/git/refs/heads"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    versions = []
    
    for item in data:
        ref = item.get("ref", "")
        if ref.startswith("refs/heads/"):
            branch_name = ref.replace("refs/heads/", "")
            if is_valid_version(branch_name):
                versions.append(branch_name)
                
    if not versions:
        raise ValueError("No valid versions found in GitHub repository.")
        
    return sort_versions(versions)

def get_available_versions(refresh: bool = False, print_warning=None) -> List[str]:
    """
    Returns the list of available versions.
    Tries to load from cache. If refresh is True or cache doesn't exist, fetches from GitHub.
    Falls back to cache or bundled list on failure.
    """
    cache_path = get_cached_versions_path()
    
    def read_cache():
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "versions" in data:
                        return sort_versions(data["versions"])
            except Exception:
                pass
        return None

    if not refresh:
        cached = read_cache()
        if cached:
            return cached

    # Attempt fetch
    try:
        versions = fetch_versions_from_github()
        # Save to cache
        cache_data = {
            "fetchedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "repository": "InventivetalentDev/minecraft-assets",
            "versions": versions
        }
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
        return versions
    except Exception:
        # Fallback
        cached = read_cache()
        if cached:
            if print_warning:
                print_warning("Could not refresh versions from GitHub. Using cached version list.")
            return cached
            
        if print_warning:
            print_warning("Could not refresh versions from GitHub. Using bundled version list.")
        return load_bundled_versions()
