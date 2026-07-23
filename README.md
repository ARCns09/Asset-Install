# Asset Install

Interactive terminal-only CLI application to download Minecraft assets from the `InventivetalentDev/minecraft-assets` repository.

## Installation

First, create a virtual environment:

```bash
python -m venv .venv
```

Next, activate the virtual environment depending on your operating system and shell:

**Windows (Command Prompt / PowerShell)**
```cmd
.venv\Scripts\activate
```

**MacOS & Linux (bash / zsh)**
```bash
source .venv/bin/activate
```

**MacOS & Linux (fish)**
```fish
source .venv/bin/activate.fish
```

Finally, install the package:
```bash
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
