from typing import List
from InquirerPy import inquirer
from InquirerPy.separator import Separator

def show_main_menu() -> str:
    """Shows the main menu and returns the selected action."""
    return inquirer.select(
        message="What would you like to do?",
        choices=[
            "Single Download",
            "Multi Download",
            "Download History",
            "Refresh Version List",
            "Exit"
        ],
        default="Single Download",
    ).execute()

def prompt_version_family(families: List[str], multi: bool = False, count: int = 0) -> str:
    """Prompts for a version family selection."""
    choices = []
    if multi:
        choices.append({"name": f"== Confirm Selection ({count} total) ==", "value": "__CONFIRM__"})
    choices.extend([{"name": f, "value": f} for f in families])
    choices.append({"name": "== Cancel ==" if multi else "== Go Back ==", "value": "__CANCEL__"})
    
    msg = "Select Minecraft Version Family:"
    return inquirer.select(message=msg, choices=choices).execute()

def prompt_single_version_in_family(family: str, versions: List[str]) -> str:
    """Prompts for a single version selection inside a family."""
    choices = [{"name": v, "value": v} for v in versions]
    choices.append({"name": "== Go Back ==", "value": "__GO_BACK__"})
    
    return inquirer.select(
        message=f"Minecraft {family}",
        choices=choices,
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

def prompt_multi_version_in_family(family: str, versions: List[str], selected: List[str] = None) -> List[str]:
    """Prompts for multi version selection within a family."""
    choices = [{"name": v, "value": v, "enabled": v in (selected or [])} for v in versions]
    
    meta_choices = [
        {"name": "== Select All (Space to select, then Enter) ==", "value": "__SELECT_ALL__"},
        {"name": "== Clear All (Space to select, then Enter) ==", "value": "__CLEAR_ALL__"},
        Separator()
    ]

    return inquirer.checkbox(
        message=f"Minecraft {family}",
        choices=meta_choices + choices,
        instruction="(Use <space> to toggle versions, <enter> to confirm and go back)"
    ).execute()

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

def prompt_clear_history() -> str:
    return inquirer.select(
        message="Clear download history? (This will not delete downloaded files)",
        choices=["Yes, clear history", "Cancel"],
        default="Cancel"
    ).execute()
