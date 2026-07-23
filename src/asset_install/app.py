import datetime
from pathlib import Path
from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

from . import menus
from .versions import get_available_versions, group_versions
from .paths import resolve_path, ensure_directory, is_path_writable
from .downloader import download_version, get_zip_url
from .manifest import Manifest
from .validator import is_valid_zip, calculate_sha256
from .history import add_history_entry, get_history, clear_history

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

def handle_single_download(groups: dict[str, list[str]]) -> list[str]:
    families = list(groups.keys())
    while True:
        family = menus.prompt_version_family(families)
        if family == "__CANCEL__":
            return []
            
        versions = groups[family]
        while True:
            selected = menus.prompt_single_version_in_family(family, versions)
            if selected == "__GO_BACK__":
                break # Go back to family picker
            
            confirm = menus.prompt_single_version_confirm(selected)
            if confirm == "Yes, continue":
                return [selected]
            elif confirm == "Cancel":
                return []
            # if Change version, loop continues in the version picker

def handle_multi_download(groups: dict[str, list[str]]) -> list[str]:
    selected_versions = set()
    families = list(groups.keys())
    
    while True:
        action = menus.prompt_version_family(families, multi=True, count=len(selected_versions))
        if action == "__CANCEL__":
            return []
        if action == "__CONFIRM__":
            if not selected_versions:
                console.print("[red]No versions selected![/red]")
                continue
            # Sort final output if needed, but they are a set.
            # We'll just return it, app will sort it later if needed.
            return list(selected_versions)
            
        family = action
        versions = groups[family]
        while True:
            current_selected = [v for v in versions if v in selected_versions]
            result = menus.prompt_multi_version_in_family(family, versions, current_selected)
            
            if "__SELECT_ALL__" in result:
                selected_versions.update(versions)
                continue
            if "__CLEAR_ALL__" in result:
                for v in versions:
                    selected_versions.discard(v)
                continue
                
            final_selection = [v for v in result if not v.startswith("__")]
            for v in versions:
                selected_versions.discard(v)
            for v in final_selection:
                selected_versions.add(v)
            break

def get_location() -> Path:
    while True:
        loc = menus.prompt_download_location()
        if loc == "Go back":
            return None
        elif loc == "Current directory":
            path = Path.cwd() / "minecraft-assets"
        elif loc == "Downloads folder":
            path = Path.home() / "Downloads" / "minecraft-assets"
        else:
            path = resolve_path(loc)
        
        if not is_path_writable(path):
            console.print(f"[red]Cannot write to {path}. Please choose another location.[/red]")
            continue
            
        return path

def show_history():
    while True:
        console.clear()
        hist = get_history()
        
        if not hist:
            console.print("[yellow]Download history is empty.[/yellow]\n")
        else:
            table = Table(title="Download History")
            table.add_column("Version", style="cyan")
            table.add_column("Date and Time", style="green")
            table.add_column("Location", style="magenta")
            
            for item in hist:
                table.add_row(item["version"], item["datetime"], item["location"])
                
            console.print(table)
            console.print("\n")
            
        action = inquirer.select(
            message="History Menu:",
            choices=["Go Back", "Clear History"] if hist else ["Go Back"]
        ).execute()
        
        if action == "Go Back":
            break
        elif action == "Clear History":
            confirm = menus.prompt_clear_history()
            if confirm == "Yes, clear history":
                clear_history()
                console.print("[green]History cleared.[/green]")

def fetch_and_warn(refresh=False):
    def print_warning(msg):
        console.print(f"[yellow]{msg}[/yellow]")
    return get_available_versions(refresh=refresh, print_warning=print_warning)

def main():
    try:
        versions = fetch_and_warn(refresh=False)
    except Exception as e:
        console.print(f"[red]Failed to load versions: {e}[/red]")
        return 1

    while True:
        console.clear()
        print_header()
        
        action = menus.show_main_menu()
        
        if action == "Exit":
            break
            
        if action == "Refresh Version List":
            console.print("[cyan]Refreshing version list from GitHub...[/cyan]")
            try:
                versions = fetch_and_warn(refresh=True)
                console.print("[green]Version list updated successfully.[/green]")
            except Exception as e:
                console.print(f"[red]Refresh failed: {e}[/red]")
            inquirer.confirm("Press Enter to continue...", default=True).execute()
            continue
            
        if action == "Download History":
            show_history()
            continue
            
        groups = group_versions(versions)
        selected_versions = []
        mode_str = ""
        
        if action == "Single Download":
            selected_versions = handle_single_download(groups)
            mode_str = "Single Download"
        elif action == "Multi Download":
            selected_versions = handle_multi_download(groups)
            # Re-sort the final selection using the main list's order
            selected_versions = [v for v in versions if v in selected_versions]
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
            continue
        elif confirm == "Change location":
            location = get_location()
            if not location:
                continue
            
            print_summary(mode_str, selected_versions, str(location))
            confirm2 = menus.prompt_final_confirmation()
            if confirm2 != "Start Download":
                continue
                
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
                        continue
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
                            continue
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
                    
                    # Local time for history
                    dt_local = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    # UTC for manifest
                    dt_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    
                    manifest.update_version(
                        version, "complete", 
                        archive=f"{version}.zip", 
                        size=downloaded_path.stat().st_size, 
                        sha256=sha256,
                        downloaded_at=dt_utc
                    )
                    
                    # Record history
                    add_history_entry(version, dt_local, str(location))
                    
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
            inquirer.confirm(message="Press Enter to return to main menu...", default=True).execute()
        elif post_action == "Exit":
            break

    return 0
