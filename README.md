# Refiny

Windows system tray app that rephrases selected text using OpenAI or Claude.
Select text anywhere, press **Ctrl+Shift+R**, pick a tone, and it replaces in place.

## How It Works

1. Press the hotkey (default **Ctrl+Shift+R**) with text selected
2. Refiny sends the text to your chosen AI provider
3. A popup shows three rephrased versions: **Friendly**, **Direct**, **Business**
4. Click **Use** (or press **1** / **2** / **3**) to replace the original text
5. Press **Esc** to cancel

All suggestions follow the [7 Cs of communication](https://en.wikipedia.org/wiki/7_Cs_of_communication) — clear, concise, and never verbose.

## Quick Start (Download)

1. Go to [Releases](../../releases) and download **Refiny.exe**
2. Run it — Refiny appears in your system tray
3. Right-click the tray icon, open **Settings**
4. Choose your API provider (OpenAI or Claude) and paste your API key
5. Select text in any app and press **Ctrl+Shift+R**

No Python installation required.

## Dev Setup (Run from Source)

Requires **Python 3.11+** on Windows.

```bat
git clone https://github.com/alejaxdiaz/Refiny.git
cd Refiny
pip install -r requirements.txt
python scripts\generate_icon.py
python -m refiny
```

`scripts\generate_icon.py` only needs to run once — it creates the tray icons in `assets/`.

## Build the .exe

```bat
build.bat
```

Installs dependencies, generates icons, and builds a standalone executable at `dist\Refiny.exe` using PyInstaller.

## Configuration

Settings are stored at `%APPDATA%\Refiny\settings.json` and managed through the Settings window (right-click tray icon > Settings).

| Setting | Options |
|---------|---------|
| **Provider** | OpenAI, Claude |
| **OpenAI models** | gpt-4o-mini, gpt-4o, gpt-4-turbo |
| **Claude models** | claude-haiku-4-5, claude-3-5-haiku, claude-sonnet-4-6, claude-opus-4-6 |
| **Hotkey** | Any key combination (default: Ctrl+Shift+R) |

## Requirements

- **Windows 10/11** (uses Win32 APIs for clipboard, window management, and system tray)
- An API key from [OpenAI](https://platform.openai.com/api-keys) or [Anthropic](https://console.anthropic.com/)

## License

[MIT](LICENSE)
