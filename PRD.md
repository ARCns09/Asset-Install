# Asset Install PRD

## 1. Product Summary

**Name:** Asset Install  
**Type:** Interactive terminal-only CLI/TUI project  
**Language:** Python 3.11+  
**Source repository:** `InventivetalentDev/minecraft-assets`  
**Purpose:** Let the user interactively choose one, several, or all supported Minecraft release versions from `1.0` through `26.2`, choose a download folder, confirm the selection, and download the selected ZIP archives one at a time.

Asset Install is not a website or desktop window. It runs entirely inside the terminal, but should feel like a small colorful terminal application rather than a command that immediately begins downloading.

The source branch format is:

```text
https://github.com/InventivetalentDev/minecraft-assets/tree/<version>
```

The ZIP archive URL is:

```text
https://github.com/InventivetalentDev/minecraft-assets/archive/refs/heads/<version>.zip
```

Example:

```text
https://github.com/InventivetalentDev/minecraft-assets/archive/refs/heads/26.2.zip
```

---

## 2. Main User Flow

Running either command should open the interactive terminal interface:

```bash
python -m asset_install
```

```bash
asset-install
```

The program must not immediately download all versions. It must first show a colorful main menu:

```text
╭──────────────────────────────╮
│        ASSET INSTALL         │
│ Minecraft Asset Downloader   │
╰──────────────────────────────╯

What would you like to do?

❯ Single Download
  Multi Download
  Exit
```

The user navigates with arrow keys and confirms with Enter.

### Single Download

1. User selects **Single Download**.
2. Show a searchable/selectable list containing every approved version from `1.0` through `26.2`.
3. User selects exactly one version.
4. Show a confirmation screen:

```text
Selected version: 1.21.11

Is this the correct version?

❯ Yes, continue
  Change version
  Cancel
```

5. If the user chooses **Change version**, return to the version picker.
6. If confirmed, ask the user to choose the download location.
7. Show a final summary.
8. Start downloading only after final confirmation.

### Multi Download

1. User selects **Multi Download**.
2. Show the full approved version list with checkboxes.
3. Allow selecting any number of versions.
4. Include a clear **Select All** option.
5. Include **Clear All** and **Confirm Selection** actions.
6. Show how many versions are currently selected.
7. After confirmation, show the complete selected-version summary.
8. Let the user return and change the selection.
9. Ask for the download location.
10. Show a final confirmation screen.
11. Download selected versions sequentially, one at a time.

Example multi-select screen:

```text
Select Minecraft versions

[ ] Select All
[ ] 1.0
[ ] 1.0.1
[ ] 1.1
[x] 1.20.6
[x] 1.21.11
[x] 26.2

Selected: 3 versions

❯ Confirm Selection
  Clear All
  Cancel
```

### Download Location

After version selection, ask where to save the ZIP files.

Provide these choices:

```text
Choose download location

❯ Current directory
  Downloads folder
  Enter custom path
  Go back
```

For a custom path:

- allow typing or pasting a path;
- expand `~`;
- show the resolved absolute path;
- create the folder only after confirmation;
- reject paths that cannot be written;
- allow the user to change the location.

Final confirmation example:

```text
Ready to download

Mode: Multi Download
Versions: 1.20.6, 1.21.11, 26.2
Total: 3 versions
Location: /home/arc/Downloads/minecraft-assets
Download order: One at a time

❯ Start Download
  Change versions
  Change location
  Cancel
```

---

## 3. Approved Release Versions

The project must include the following exact list in:

```text
config/versions.txt
```

```text
1.0
1.0.1
1.1
1.2
1.2.1
1.2.2
1.2.3
1.2.4
1.2.5
1.3
1.3.1
1.3.2
1.4
1.4.2
1.4.4
1.4.5
1.4.6
1.4.7
1.5
1.5.1
1.5.2
1.6
1.6.1
1.6.2
1.6.4
1.7
1.7.2
1.7.10
1.8
1.8.1
1.8.2
1.8.3
1.8.4
1.8.5
1.8.6
1.8.7
1.8.8
1.8.9
1.9
1.9.1
1.9.2
1.9.4
1.10
1.10.1
1.10.2
1.11
1.11.1
1.11.2
1.12
1.12.1
1.12.2
1.13
1.13.1
1.13.2
1.14
1.14.1
1.14.2
1.14.3
1.14.4
1.15
1.15.1
1.15.2
1.16
1.16.1
1.16.2
1.16.3
1.16.4
1.16.5
1.17
1.17.1
1.18
1.18.1
1.18.2
1.19
1.19.1
1.19.2
1.19.3
1.19.4
1.20
1.20.1
1.20.2
1.20.3
1.20.4
1.20.5
1.20.6
1.21
1.21.1
1.21.2
1.21.3
1.21.4
1.21.5
1.21.6
1.21.7
1.21.8
1.21.9
1.21.10
1.21.11
26.1
26.1.1
26.1.2
26.2
```

Rules:

- one version per line;
- preserve this exact order;
- blank lines may be ignored;
- no automatic additions;
- no snapshots or joke versions;
- a missing GitHub branch must be reported clearly and skipped;
- the tool must not silently alter a version string.


---

## 4. Terminal Interface Requirements

Use a lightweight colorful terminal UI.

Recommended libraries:

- `rich` for colors, panels, progress bars, and summaries;
- `questionary`, `InquirerPy`, or an equivalent maintained library for arrow-key menus, checkboxes, confirmations, and path prompts.

The interface should:

- work in a normal Linux terminal;
- use a small tasteful color palette;
- remain readable without color;
- support arrow keys and Enter;
- support Space for checkbox selection;
- support typing to filter the version list;
- clearly highlight the current selection;
- never require the user to remember command flags;
- handle Ctrl+C cleanly and return to the shell;
- avoid mouse-only controls;
- avoid full-screen complexity when a simple prompt is enough.

This is a terminal TUI, not a graphical desktop GUI.

---

## 5. Download Behavior

Downloads must run sequentially.

Only one version may download at a time.

For each selected version:

1. construct the exact branch ZIP URL;
2. create `<version>.zip.part` in the chosen destination;
3. stream the response to disk;
4. follow GitHub redirects;
5. show live progress, speed, downloaded size, and percentage when available;
6. retry temporary failures up to three times;
7. validate the completed file as a readable ZIP;
8. calculate SHA-256;
9. atomically rename `<version>.zip.part` to `<version>.zip`;
10. record the result in a manifest;
11. continue to the next selected version.

Example:

```text
Downloading 2 of 3

Minecraft 1.21.11
██████████████████░░░░░░ 74%
86.5 MiB / 116.9 MiB
5.7 MiB/s

Completed: 1
Remaining: 2
```

Do not run multiple downloads concurrently.

---

## 6. Existing File Handling

When `<version>.zip` already exists in the chosen folder:

```text
1.21.11.zip already exists.

❯ Skip this version
  Verify and use existing file
  Replace existing file
  Cancel remaining downloads
```

Recommended default:

- verify the existing ZIP;
- compare SHA-256 with the local manifest when available;
- use it when valid;
- replace it only when invalid or explicitly requested.

The program must never overwrite a valid archive silently.

---

## 7. Output Layout

The user chooses the root download location.

Inside that location, Asset Install should create:

```text
minecraft-assets/
├── 1.0.zip
├── 1.0.1.zip
├── 1.21.11.zip
├── 26.2.zip
├── manifest.json
└── asset-install.log
```

Incomplete downloads remain as:

```text
1.21.11.zip.part
```

Do not extract archives. RP-Templates / MC-Vault can process them later.

---

## 8. Manifest

Create:

```text
manifest.json
```

Example:

```json
{
  "repository": "InventivetalentDev/minecraft-assets",
  "downloadDirectory": "/home/arc/Downloads/minecraft-assets",
  "versions": {
    "26.2": {
      "source": "https://github.com/InventivetalentDev/minecraft-assets/archive/refs/heads/26.2.zip",
      "archive": "26.2.zip",
      "status": "complete",
      "size": 123456,
      "sha256": "hex-value",
      "downloadedAt": "ISO-8601 timestamp",
      "error": null
    }
  }
}
```

Possible statuses:

- `pending`
- `downloading`
- `complete`
- `skipped`
- `failed`
- `cancelled`

Write the manifest atomically.

---

## 9. Download Completion Screen

After all selected versions finish, show a clean summary:

```text
╭──────────────────────────────╮
│      DOWNLOAD COMPLETE       │
╰──────────────────────────────╯

Downloaded: 3
Skipped: 0
Failed: 0

Saved to:
/home/arc/Downloads/minecraft-assets

❯ Open folder path
  Return to main menu
  Exit
```

Since this is a terminal utility, **Open folder path** may print the exact path. It should not require launching a graphical file manager.

When failures occur, list the exact versions and reasons.

---

## 10. Error Handling

Retry:

- connection resets;
- temporary DNS failures;
- HTTP 429;
- HTTP 500;
- HTTP 502;
- HTTP 503;
- HTTP 504.

Do not repeatedly retry:

- HTTP 404;
- missing branch;
- corrupted ZIP after repeated download;
- permission errors;
- insufficient storage;
- invalid destination path.

A failed version must not stop later selected versions unless the user chooses to cancel.

After a failure:

```text
Failed to download 1.14.2
Reason: GitHub returned HTTP 404

❯ Continue with remaining versions
  Retry this version
  Cancel remaining downloads
```

---

## 11. Security Requirements

- Never run downloaded files.
- Never invoke shell commands using version input.
- Treat downloaded archives as data only.
- URL-encode refs.
- Use only versions from the built-in approved list.
- Never trust remote filenames.
- Write only inside the confirmed destination.
- Never expose tokens in logs.
- Never delete unrelated files.
- Never substitute `master`, `latest`, or another version when a branch is missing.
- Public GitHub downloads must work without authentication.

---

## 12. Project Structure

```text
asset-install/
├── PRD.md
├── README.md
├── pyproject.toml
├── config/
│   └── versions.txt
├── src/
│   └── asset_install/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── menus.py
│       ├── versions.py
│       ├── downloader.py
│       ├── manifest.py
│       ├── validator.py
│       └── paths.py
└── tests/
```

---

## 13. Installation and Launch

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
asset-install
```

The installed `asset-install` command should always open the interactive main menu.

Optional non-interactive command flags are not required for the first release.

---

## 14. Testing Requirements

Tests must cover:

- loading the full approved version list;
- single-selection flow;
- multi-selection flow;
- Select All;
- Clear All;
- confirmation and change-selection paths;
- destination selection;
- unwritable destination rejection;
- correct branch ZIP URL construction;
- redirects;
- sequential download ordering;
- interrupted `.part` download;
- retryable network failure;
- HTTP 404;
- corrupted ZIP;
- existing-file choice flow;
- SHA-256 generation;
- atomic manifest writes;
- Ctrl+C cancellation.

Use a local test HTTP server for automated download tests.

Perform at least one real GitHub download as a final manual acceptance test.

---

## 15. Completion Criteria

The project is complete only when:

- launching it opens a colorful interactive terminal menu;
- Single Download allows exactly one version;
- Multi Download allows many versions;
- Select All works;
- the user can change the selection before downloading;
- the user chooses and confirms the destination;
- the final summary is shown before downloads begin;
- versions download one at a time;
- live progress is readable;
- `.part` files protect incomplete downloads;
- completed ZIPs are validated;
- SHA-256 and results are saved;
- failures do not silently stop the full queue;
- all supported versions remain limited to the approved `1.0` through `26.2` list;
- no auto-discovery exists;
- no website, desktop GUI, database, scheduler, or multi-phase roadmap is added;
- tests and README are complete.

---

## 16. Final Instruction for the Coding Agent

Implement Asset Install as one finished interactive terminal application.

Do not stop after scaffolding and do not divide the work into phases.

The final experience should be simple:

```text
Open Asset Install
→ Choose Single or Multi Download
→ Select version or versions
→ Confirm selection
→ Choose download folder
→ Confirm everything
→ Download ZIP files one at a time
→ Show completion summary
```

Do not install system packages or use `sudo`.

Do not push to GitHub or create commits unless explicitly requested.
