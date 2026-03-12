# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run

```bat
# Full build (install deps → generate icons → build exe):
build.bat
# Output: dist\Refiny.exe (standalone, console=False)

# Dev run (requires Python + deps installed):
pip install -r requirements.txt
python scripts\generate_icon.py   # one-time: creates assets/icon.png + icon_gray.png + .ico
python -m refiny

# PyInstaller spec lives at build\Refiny.spec — edit there for bundled assets or hiddenimports
```

No test suite exists. No linter is configured.

## Project Structure

```
refiny/              # Python package — all app source code
  __main__.py        # entry point for `python -m refiny`
  main.py            # bootstrap: hidden tkinter root, tray thread, hotkey manager
  api_client.py      # OpenAI + Claude abstraction
  clipboard.py       # pywin32 backup/restore CF_UNICODETEXT
  hotkey.py          # global hotkey via `keyboard` lib
  loading.py         # loading indicator near cursor
  popup.py           # dark frameless popup with 3 tone cards
  replacer.py        # SetForegroundWindow + Ctrl+V paste-back
  settings.py        # JSON config at %APPDATA%\Refiny\settings.json
  settings_ui.py     # Settings window UI
  tray.py            # pystray system tray icon
scripts/
  generate_icon.py   # run once to create assets/icon.png + icon_gray.png
assets/              # generated icon files (committed, needed for build)
build/
  Refiny.spec        # PyInstaller config
```

## Architecture

Refiny is a **Windows-only** system tray app that rephrases selected text via LLM APIs. The flow:

1. **Hotkey press** (`refiny/hotkey.py`) — `keyboard` lib captures global hotkey (default Ctrl+Shift+R, `suppress=True`). Records the foreground window handle and cursor position, shows a loading indicator, then simulates Ctrl+C via pynput to grab the selection.
2. **Clipboard dance** (`refiny/clipboard.py`) — pywin32 `CF_UNICODETEXT` backup → read copied text → will restore original clipboard after use.
3. **API call** (`refiny/api_client.py`) — sends text to OpenAI or Claude with a system prompt enforcing the 7 Cs. Returns `{"friendly": ..., "direct": ..., "business": ...}` parsed from JSON. Errors are mapped to named `APIError` codes (`no_key`, `invalid_key`, `rate_limit`, etc.).
4. **Popup** (`refiny/popup.py`) — frameless dark Toplevel with 3 tone cards. User picks via click or keyboard 1/2/3. Escape or focus-out dismisses.
5. **Replace** (`refiny/replacer.py`) — sets clipboard to chosen text, `SetForegroundWindow` back to the original app, simulates Ctrl+V, then restores the original clipboard on a background thread after 500ms.

**Threading model**: tkinter main loop runs on the main thread (`_root.mainloop()`). Pystray tray runs on a daemon thread. API calls run on daemon threads. All UI updates go through `_root.after()` for thread safety.

**Settings**: JSON at `%APPDATA%\Refiny\settings.json`. Defaults defined in `refiny/settings.py:DEFAULTS`. The settings UI (`refiny/settings_ui.py`) swaps provider-specific fields (key + model list) when toggling between OpenAI and Claude.

## Key Constraints

- Windows-only: uses `win32gui`, `win32clipboard`, `win32api`, `pystray._win32`
- Final artifact is a `.exe` — no console window (`console=False` in spec)
- All 3 suggestions displayed simultaneously; user clicks [Use] to replace in-place
- API responses must be concise (7 Cs enforced; never verbose)
- `keyboard` lib requires `suppress=True` for the global hotkey to work reliably
- Icon assets (`assets/icon.png`, `icon_gray.png`, `icon.ico`) must exist before building — `scripts/generate_icon.py` creates them
- Internal imports use relative style (`from . import clipboard`) since source lives in the `refiny` package
