import sys
from .app import main as run_application

__version__ = "1.0.0"

def main() -> int:
    if len(sys.argv) > 1:
        if sys.argv[1] in ("--help", "-h"):
            print("Usage: mc-asset")
            print("\nInteractive terminal Minecraft Asset Downloader.")
            return 0
        elif sys.argv[1] in ("--version", "-v"):
            print(f"mc-asset {__version__}")
            return 0
        else:
            print(f"Error: Unknown argument '{sys.argv[1]}'")
            return 1
            
    try:
        run_application()
        return 0
    except KeyboardInterrupt:
        return 130
