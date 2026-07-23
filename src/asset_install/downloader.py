import os
import requests
import time
from pathlib import Path
from urllib.parse import quote

from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

def get_zip_url(version: str) -> str:
    """Constructs the ZIP URL for a given version."""
    encoded_version = quote(version)
    return f"https://github.com/InventivetalentDev/minecraft-assets/archive/refs/heads/{encoded_version}.zip"

class DownloadError(Exception):
    pass

class NonRetryableError(DownloadError):
    pass

class RetryableError(DownloadError):
    pass

def download_version(version: str, dest_dir: Path, progress: Progress) -> Path:
    """
    Downloads the ZIP archive for the given version.
    Returns the final Path of the downloaded ZIP.
    Raises DownloadError on failure.
    """
    url = get_zip_url(version)
    final_path = dest_dir / f"{version}.zip"
    part_path = dest_dir / f"{version}.zip.part"
    
    max_retries = 3
    retries = 0
    
    while retries <= max_retries:
        try:
            with requests.get(url, stream=True, timeout=15) as response:
                if response.status_code == 404:
                    raise NonRetryableError("GitHub returned HTTP 404 (Branch not found)")
                if response.status_code in (429, 500, 502, 503, 504):
                    raise RetryableError(f"HTTP {response.status_code}")
                
                response.raise_for_status()
                
                content_length = response.headers.get("content-length")
                total_size = int(content_length) if content_length is not None else None
                
                task_id = progress.add_task(f"[cyan]Minecraft {version}", total=total_size)
                
                with open(part_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(task_id, advance=len(chunk))
                
                # Download complete, rename part to final
                os.replace(part_path, final_path)
                return final_path
                
        except RetryableError as e:
            retries += 1
            if retries > max_retries:
                raise DownloadError(f"Failed after {max_retries} retries. Last error: {e}")
            time.sleep(2 ** retries) # Exponential backoff
        except requests.exceptions.RequestException as e:
            # For network-level errors (connection reset, DNS, timeout)
            retries += 1
            if retries > max_retries:
                raise DownloadError(f"Network error after {max_retries} retries: {e}")
            time.sleep(2 ** retries)
            
    raise DownloadError("Unknown error occurred")
