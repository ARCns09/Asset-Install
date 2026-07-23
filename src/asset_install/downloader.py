import os
import requests
import time
from pathlib import Path
from urllib.parse import quote

from rich.progress import Progress

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
        headers = {}
        initial_size = 0
        if part_path.exists():
            initial_size = part_path.stat().st_size
            if initial_size > 0:
                headers["Range"] = f"bytes={initial_size}-"
                
        try:
            with requests.get(url, headers=headers, stream=True, timeout=15) as response:
                if response.status_code == 404:
                    raise NonRetryableError("GitHub returned HTTP 404 (Branch not found)")
                if response.status_code in (429, 500, 502, 503, 504):
                    raise RetryableError(f"HTTP {response.status_code}")
                if response.status_code == 416: # Range Not Satisfiable
                    part_path.unlink()
                    continue
                
                response.raise_for_status()
                
                is_resume = response.status_code == 206
                if not is_resume and initial_size > 0:
                    # Server ignored Range or it changed. Start over.
                    initial_size = 0
                
                content_length = response.headers.get("content-length")
                if content_length is not None:
                    total_size = initial_size + int(content_length)
                else:
                    total_size = None
                
                task_id = progress.add_task(f"[cyan]Minecraft {version}", total=total_size)
                if initial_size > 0:
                    progress.update(task_id, advance=initial_size)
                
                mode = "ab" if is_resume else "wb"
                with open(part_path, mode) as f:
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
