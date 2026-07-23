import json
from pathlib import Path
from typing import List, Dict

from .paths import get_app_data_dir

def get_history_path() -> Path:
    return get_app_data_dir() / "history.json"

def get_history() -> List[Dict[str, str]]:
    """Loads history, newest first."""
    path = get_history_path()
    if not path.exists():
        return []
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("history", [])
    except Exception:
        return []

def add_history_entry(version: str, dt_str: str, location: str):
    """Adds a new download to the history (prepends it so newest is first)."""
    history = get_history()
    
    entry = {
        "version": version,
        "datetime": dt_str,
        "location": location
    }
    
    history.insert(0, entry) # Prepend
    
    path = get_history_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"history": history}, f, indent=2)

def clear_history():
    """Clears all history entries."""
    path = get_history_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"history": []}, f)
