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

def prompt_final_confirmation(choices: List[str] = None) -> str:
    """Prompts the final confirmation before download."""
    if choices is None:
        choices = [
            "Start Download",
            "Change versions",
            "Change location",
            "Cancel"
        ]
        
    return inquirer.select(
        message="Ready to download",
        choices=choices,
        default="Start Download"
    ).execute()

def prompt_output_mode(default_mode: str = "Original ZIP only") -> str:
    """Prompts the user to choose an output mode."""
    return inquirer.select(
        message="Choose Download Output",
        choices=[
            "Original ZIP only",
            "Filtered Resource Pack only",
            "Go Back"
        ],
        default=default_mode
    ).execute()

def prompt_asset_categories(selected_categories: set) -> str:
    """Prompts the user to toggle categories using a looping select menu."""
    from .extractor import CATEGORY_MAP
    categories = list(CATEGORY_MAP.keys()) + ["Other Resource-Pack Assets"]
    
    while True:
        choices = [
            {"name": "Continue", "value": "__CONTINUE__"},
            {"name": "Select All", "value": "__SELECT_ALL__"},
            {"name": "Clear All", "value": "__CLEAR_ALL__"},
            {"name": "Go Back", "value": "__GO_BACK__"},
            Separator()
        ]
        
        for c in categories:
            prefix = "[x]" if c in selected_categories else "[ ]"
            choices.append({"name": f"{prefix} {c}", "value": c})
            
        action = inquirer.select(
            message="Choose Resource-Pack Assets (Enter to toggle/select)",
            choices=choices
        ).execute()
        
        if action == "__CONTINUE__":
            return "continue"
        elif action == "__GO_BACK__":
            return "back"
        elif action == "__SELECT_ALL__":
            selected_categories.update(categories)
        elif action == "__CLEAR_ALL__":
            selected_categories.clear()
        else:
            if action in selected_categories:
                selected_categories.discard(action)
            else:
                selected_categories.add(action)

def prompt_texture_subcategories(selected_subs: set) -> str:
    """Prompts the user to toggle texture sub-categories using a looping select menu."""
    from .extractor import TEXTURE_SUB_MAP
    categories = list(TEXTURE_SUB_MAP.keys()) + ["Other Textures"]
    
    while True:
        choices = [
            {"name": "Continue", "value": "__CONTINUE__"},
            {"name": "Select All", "value": "__SELECT_ALL__"},
            {"name": "Clear All", "value": "__CLEAR_ALL__"},
            {"name": "Go Back", "value": "__GO_BACK__"},
            Separator()
        ]
        
        for c in categories:
            prefix = "[x]" if c in selected_subs else "[ ]"
            choices.append({"name": f"{prefix} {c}", "value": c})
            
        action = inquirer.select(
            message="Choose Texture Assets (Enter to toggle/select)",
            choices=choices
        ).execute()
        
        if action == "__CONTINUE__":
            return "continue"
        elif action == "__GO_BACK__":
            return "back"
        elif action == "__SELECT_ALL__":
            selected_subs.update(categories)
        elif action == "__CLEAR_ALL__":
            selected_subs.clear()
        else:
            if action in selected_subs:
                selected_subs.discard(action)
            else:
                selected_subs.add(action)

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
