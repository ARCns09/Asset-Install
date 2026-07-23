from pathlib import Path
from typing import List, Optional

from InquirerPy import inquirer
from InquirerPy.validator import PathValidator

from .paths import resolve_path, is_path_writable
from .versions import get_approved_versions

def show_main_menu() -> str:
    """Shows the main menu and returns the selected action."""
    return inquirer.select(
        message="What would you like to do?",
        choices=[
            "Single Download",
            "Multi Download",
            "Exit"
        ],
        default="Single Download",
    ).execute()

def prompt_single_version(versions: List[str]) -> str:
    """Prompts for a single version selection with search."""
    return inquirer.fuzzy(
        message="Select a version:",
        choices=versions,
    ).execute()

def prompt_single_version_confirm(version: str) -> str:
    """Confirms the selected single version."""
    return inquirer.select(
        message=f"Selected version: {version}\n\nIs this the correct version?",
        choices=[
            "Yes, continue",
            "Change version",
            "Cancel"
        ],
        default="Yes, continue"
    ).execute()

def prompt_multi_version(versions: List[str], selected: List[str] = None) -> List[str]:
    """Prompts for multi version selection. Includes Select All/Clear All handling."""
    choices = [{"name": v, "value": v, "enabled": v in (selected or [])} for v in versions]
    
    # We can't natively add a distinct action button inside checkbox using just InquirerPy's checkbox, 
    # but we can add meta-options at the top.
    
    meta_choices = [
        {"name": "== Confirm Selection ==", "value": "__CONFIRM__"},
        {"name": "== Select All ==", "value": "__SELECT_ALL__"},
        {"name": "== Clear All ==", "value": "__CLEAR_ALL__"},
        {"name": "== Cancel ==", "value": "__CANCEL__"},
        inquirer.separator()
    ]

    result = inquirer.checkbox(
        message="Select Minecraft versions (Space to toggle, Enter to finish)",
        choices=meta_choices + choices,
        instruction="(Press <space> to select, <enter> to finish)"
    ).execute()

    return result

def prompt_download_location() -> str:
    """Prompts the user for the download location."""
    action = inquirer.select(
        message="Choose download location:",
        choices=[
            "Current directory",
            "Downloads folder",
            "Enter custom path",
            "Go back"
        ],
        default="Current directory"
    ).execute()
    
    if action == "Enter custom path":
        return inquirer.filepath(
            message="Enter custom path:",
            validate=lambda p: len(p) > 0,
            invalid_message="Path cannot be empty"
        ).execute()
    return action

def prompt_final_confirmation() -> str:
    """Prompts the final confirmation before download."""
    return inquirer.select(
        message="Ready to download",
        choices=[
            "Start Download",
            "Change versions",
            "Change location",
            "Cancel"
        ],
        default="Start Download"
    ).execute()

def prompt_existing_file(filename: str) -> str:
    """Prompts when a file already exists."""
    return inquirer.select(
        message=f"{filename} already exists.",
        choices=[
            "Skip this version",
            "Verify and use existing file",
            "Replace existing file",
            "Cancel remaining downloads"
        ],
        default="Verify and use existing file"
    ).execute()

def prompt_failure_continue(version: str, reason: str) -> str:
    """Prompts when a download fails."""
    return inquirer.select(
        message=f"Failed to download {version}\nReason: {reason}",
        choices=[
            "Continue with remaining versions",
            "Retry this version",
            "Cancel remaining downloads"
        ],
        default="Continue with remaining versions"
    ).execute()
