# Asset Install

Interactive terminal-only CLI application to download Minecraft assets from the `InventivetalentDev/minecraft-assets` repository.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

Run the following command to open the interactive UI:

```bash
asset-install
```

Or run via python module:

```bash
python -m asset_install
```

## Features
- Single or Multi version downloading
- Resumes downloads using `.zip.part` logic
- Checksums files with SHA-256
- Colorful terminal interface using `rich` and `InquirerPy`
