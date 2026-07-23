# Asset Install

Interactive terminal-only CLI application to download Minecraft assets from the `InventivetalentDev/minecraft-assets` repository.

## Overview
Asset Install is a real cross-platform command-line application that allows you to cleanly download exact original assets from any historical version of Minecraft Java Edition.

## Features
- Single or Multi version downloading
- Resumes downloads using `.zip.part` logic
- Checksums files with SHA-256
- Hierarchical version navigation
- Automatic GitHub version retrieval and bundled fallback
- Colorful terminal interface using `rich` and `InquirerPy`

## Installation

Asset Install can be installed as a command-line tool using `uv`.

### 1. Install uv

Linux and macOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart the terminal if `uv` is not immediately available.

### 2. Install Asset Install

```bash
uv tool install git+https://github.com/ARCns09/Asset-Install.git
```

### 3. Launch

```bash
mc-asset
```

The command can be run from any directory.

## Run Without Installing

```bash
uvx --from git+https://github.com/ARCns09/Asset-Install.git mc-asset
```

This runs Asset Install in an isolated temporary environment without permanently installing the command.

## Usage

Open the application:

```bash
mc-asset
```

Show help:

```bash
mc-asset --help
```

Show the installed version:

```bash
mc-asset --version
```

## Updating

```bash
uv tool upgrade mc-asset
```

## Uninstalling

```bash
uv tool uninstall mc-asset
```

## Developer Setup

Clone the repository:

```bash
git clone https://github.com/ARCns09/Asset-Install.git
cd Asset-Install
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Linux and macOS:

```bash
source .venv/bin/activate
```

Fish:

```fish
source .venv/bin/activate.fish
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install in editable mode:

```bash
pip install -e .
```

Run:

```bash
mc-asset
```

## Troubleshooting
If you encounter errors related to missing commands after installing with `uv tool`, make sure your `~/.local/bin` (Linux/macOS) or `%USERPROFILE%\.local\bin` (Windows) is added to your system's `PATH`.
