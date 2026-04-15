# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Script

```bash
# Run with default settings (Microsoft Edge + FeHelper extension)
python pattern.py "Microsoft Edge" "chrome-extension://feolnkbgcbjmamimpfcnklggdcbgakhe/json-format/index.html"

# The script reads from and writes to the system clipboard, then opens the browser via AppleScript.
# Requires: pip install pyperclip
```

The Alfred workflow invokes this script via the Python interpreter at:
`/Users/niujianyu/Desktop/Develop/mai/venv3/bin/python`

## Architecture

This is a single-file Alfred Workflow with one Python script (`pattern.py`) and one Alfred config (`info.plist`).

**Data flow:**
1. Alfred keyword `json` triggers `pattern.py` via `alfred.workflow.action.script`
2. `pattern.py` reads the clipboard, applies regex transforms, writes back to clipboard, then uses `osascript` to open a FeHelper tab in Edge and paste the content

**The transforms in `pattern.py` (in order):**
- Python literals → JSON-safe strings: `None`, `True`, `False` → quoted strings
- Triple-quoted strings `"""..."""` → standard double-quoted strings
- `datetime.datetime(y, m, d, H, M, S)` → `"YYYY-MM-DD HH:MM:SS"`
- `datetime.date(y, m, d)` → `"YYYY-MM-DD"`
- Newline-separated plain text (words/numbers only) → JSON array `[...]`

**Browser/URL are parameterized** — the first CLI arg is the application name (AppleScript target), the second is the URL to open.
