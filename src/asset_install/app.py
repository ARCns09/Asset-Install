import sys
import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

from . import menus
from InquirerPy import inquirer
from .versions import get_approved_versions
from .paths import resolve_path, ensure_directory, is_path_writable
from .downloader import download_version, DownloadError, get_zip_url
from .manifest import Manifest
from .validator import is_valid_zip, calculate_sha256

console = Console()

def print_header():
    console.print(Panel(
        Text("ASSET INSTALL\nMinecraft Asset Downloader", justify="center", style="bold cyan"),
        width=40
    ))

def print_summary(mode: str, versions: list[str], location: str):
    console.print("\n[bold]Ready to download[/bold]")
    console.print(f"Mode: {mode}")
    if len(versions) <= 5:
        console.print(f"Versions: {', '.join(versions)}")
    else:
        console.print(f"Versions: {', '.join(versions[:5])} ... and {len(versions) - 5} more")
    console.print(f"Total: {len(versions)} versions")
    console.print(f"Location: {location}")
    console.print("Download order: One at a time\n")

def handle_single_download(versions: list[str]) -> list[str]:
    while True:
        selected = menus.prompt_single_version(versions)
        if not selected:
            return []
        
        confirm = menus.prompt_single_version_confirm(selected)
        if confirm == "Yes, continue":
            return [selected]
        elif confirm == "Cancel":
            return []
        # if Change version, loop continues

def handle_multi_download(versions: list[str]) -> list[str]:
    selected_versions = []
    while True:
        result = menus.prompt_multi_version(versions, selected_versions)
        
        # Handle special actions
        if "__CANCEL__" in result:
            return []
        if "__CLEAR_ALL__" in result:
            selected_versions = []
            continue
        if "__SELECT_ALL__" in result:
            selected_versions = versions.copy()
            continue
        if "__CONFIRM__" in result:
            # Filter out special actions
            final_selection = [v for v in result if not v.startswith("__")]
            if not final_selection:
                console.print("[red]No versions selected![/red]")
                selected_versions = []
                continue
            return final_selection
            
        # Update selection and loop back
        selected_versions = [v for v in result if not v.startswith("__")]

def get_location() -> Path:
    while True:
        loc = menus.prompt_download_location()
        if loc == "Go back":
            return None
        elif loc == "Current directory":
            path = Path.cwd() / "minecraft-assets"
        elif loc == "Downloads folder":
            path = Path.home() / "Downloads" / "minecraft-assets"
        else: # Custom path
            path = resolve_path(loc)
        
        if not is_path_writable(path):
            console.print(f"[red]Cannot write to {path}. Please choose another location.[/red]")
            continue
            
        return path

def process_downloads(versions: list[str], location: Path):
    ensure_directory(location)
    manifest = Manifest(location)
    
    downloaded = 0
    skipped = 0
    failed = 0
    
    total = len(versions)
    
    for i, version in enumerate(versions, 1):
        console.print(f"\n[bold]Processing {i} of {total}: Minecraft {version}[/bold]")
        
        final_path = location / f"{version}.zip"
        
        # Check existing file
        if final_path.exists():
            action = menus.prompt_existing_file(f"{version}.zip")
            if action == "Cancel remaining downloads":
                break
            elif action == "Skip this version":
                manifest.update_version(version, "skipped")
                skipped += 1
                continue
            elif action == "Verify and use existing file":
                if is_valid_zip(final_path):
                    console.print("[green]Existing file is valid.[/green]")
                    sha256 = calculate_sha256(final_path)
                    size = final_path.stat().st_size
                    manifest.update_version(
                        version, "complete", 
                        archive=f"{version}.zip", 
                        size=size, 
                        sha256=sha256
                    )
                    skipped += 1
                    continue
                else:
                    console.print("[yellow]Existing file is invalid. Re-downloading.[/yellow]")
            # If "Replace existing file" or invalid, we just continue to download
        
        manifest.update_version(version, "downloading", source=get_zip_url(version))
        
        try:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn()
            ) as progress:
                downloaded_path = download_version(version, location, progress)
            
            if not is_valid_zip(downloaded_path):
                raise Exception("Downloaded file is not a valid ZIP archive")
                
            sha256 = calculate_sha256(downloaded_path)
            size = downloaded_path.stat().st_size
            dt = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            manifest.update_version(
                version, "complete", 
                archive=f"{version}.zip", 
                size=size, 
                sha256=sha256,
                downloaded_at=dt
            )
            downloaded += 1
            console.print(f"[green]Successfully downloaded {version}[/green]")
            
        except Exception as e:
            manifest.update_version(version, "failed", error=str(e))
            failed += 1
            
            action = menus.prompt_failure_continue(version, str(e))
            if action == "Cancel remaining downloads":
                break
            elif action == "Retry this version":
                # A proper implementation would retry the loop for this version, 
                # but to keep it simple we'll just fail it and let user re-run
                # Or we can insert it back at the front of the list
                # For this PRD, we just ask, and if retry we could use a while loop inside.
                # Let's fix this logic to support retry.
                pass # Will implement retry logic inside a loop below in a refactor
            
            # Since the structure is already simple, we'll just continue if they choose "Continue"
            # If they choose Retry, we'll have to adjust. Let's adjust the structure.

    # Print summary
    console.print("\n" + "="*30)
    console.print(Panel(Text("DOWNLOAD COMPLETE", justify="center", style="bold green"), width=40))
    console.print(f"Downloaded: {downloaded}")
    console.print(f"Skipped: {skipped}")
    console.print(f"Failed: {failed}")
    console.print(f"\nSaved to:\n{location}\n")
    
    # We shouldn't use sys.exit here directly if they want to return to menu, but for simplicity let's just finish.
    # The PRD says:
    # > Open folder path
    # > Return to main menu
    # > Exit
    
    # We will implement that in the main loop.

def main():
    try:
        versions = get_approved_versions()
    except Exception as e:
        console.print(f"[red]Failed to load versions: {e}[/red]")
        return 1

    while True:
        console.clear()
        print_header()
        
        action = menus.show_main_menu()
        
        if action == "Exit":
            break
            
        selected_versions = []
        mode_str = ""
        
        if action == "Single Download":
            selected_versions = handle_single_download(versions)
            mode_str = "Single Download"
        elif action == "Multi Download":
            selected_versions = handle_multi_download(versions)
            mode_str = "Multi Download"
            
        if not selected_versions:
            continue
            
        location = get_location()
        if not location:
            continue
            
        print_summary(mode_str, selected_versions, str(location))
        
        confirm = menus.prompt_final_confirmation()
        
        if confirm == "Cancel":
            continue
        elif confirm == "Change versions":
            # Just loop back, they'll have to pick again. For a better UX we could jump to the picker.
            continue
        elif confirm == "Change location":
            location = get_location()
            if not location: continue
            
            print_summary(mode_str, selected_versions, str(location))
            confirm2 = menus.prompt_final_confirmation()
            if confirm2 != "Start Download":
                continue
                
        # Now we process
        ensure_directory(location)
        manifest = Manifest(location)
        
        downloaded = 0
        skipped = 0
        failed = 0
        total = len(selected_versions)
        
        cancel_all = False
        
        for i, version in enumerate(selected_versions, 1):
            if cancel_all:
                break
                
            retry = True
            while retry:
                retry = False
                console.print(f"\n[bold]Processing {i} of {total}: Minecraft {version}[/bold]")
                
                final_path = location / f"{version}.zip"
                
                if final_path.exists():
                    exist_action = menus.prompt_existing_file(f"{version}.zip")
                    if exist_action == "Cancel remaining downloads":
                        cancel_all = True
                        break
                    elif exist_action == "Skip this version":
                        manifest.update_version(version, "skipped")
                        skipped += 1
                        continue # next version
                    elif exist_action == "Verify and use existing file":
                        if is_valid_zip(final_path):
                            console.print("[green]Existing file is valid.[/green]")
                            sha256 = calculate_sha256(final_path)
                            manifest.update_version(
                                version, "complete", 
                                archive=f"{version}.zip", 
                                size=final_path.stat().st_size, 
                                sha256=sha256
                            )
                            skipped += 1
                            continue # next version
                        else:
                            console.print("[yellow]Existing file is invalid. Re-downloading.[/yellow]")
                
                manifest.update_version(version, "downloading", source=get_zip_url(version))
                
                try:
                    with Progress(
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(),
                        DownloadColumn(binary_units=True),
                        TransferSpeedColumn(),
                        TimeRemainingColumn()
                    ) as progress:
                        downloaded_path = download_version(version, location, progress)
                    
                    if not is_valid_zip(downloaded_path):
                        raise Exception("Downloaded file is not a valid ZIP archive")
                        
                    sha256 = calculate_sha256(downloaded_path)
                    dt = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    manifest.update_version(
                        version, "complete", 
                        archive=f"{version}.zip", 
                        size=downloaded_path.stat().st_size, 
                        sha256=sha256,
                        downloaded_at=dt
                    )
                    downloaded += 1
                    console.print(f"[green]Successfully downloaded {version}[/green]")
                    
                except Exception as e:
                    manifest.update_version(version, "failed", error=str(e))
                    fail_action = menus.prompt_failure_continue(version, str(e))
                    if fail_action == "Cancel remaining downloads":
                        cancel_all = True
                        break
                    elif fail_action == "Retry this version":
                        retry = True
                        continue
                    elif fail_action == "Continue with remaining versions":
                        failed += 1
                        continue
                        
        console.print("\n" + "─"*30)
        console.print(Panel(Text("DOWNLOAD COMPLETE", justify="center", style="bold green"), width=40))
        console.print(f"Downloaded: {downloaded}")
        console.print(f"Skipped: {skipped}")
        console.print(f"Failed: {failed}")
        console.print(f"\nSaved to:\n{location}\n")
        
        post_action = inquirer.select(
            message="What's next?",
            choices=[
                "Open folder path",
                "Return to main menu",
                "Exit"
            ],
            default="Return to main menu"
        ).execute()
        
        if post_action == "Open folder path":
            console.print(f"\n[cyan]{location}[/cyan]\n")
            # Wait for user acknowledgment
            inquirer.confirm(message="Press Enter to return to main menu...", default=True).execute()
        elif post_action == "Exit":
            break

    return 0
