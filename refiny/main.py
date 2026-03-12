"""Refiny — lightweight text rephrasing app.
Runs as a Windows system tray app. No console window.
"""
import threading
import tkinter as tk

from . import api_client
from . import clipboard as cb
from . import hotkey as hk_module
from . import loading as loading_module
from . import replacer
from . import settings as cfg
from . import tray as tray_module
from .popup import show as show_popup
from .settings_ui import SettingsWindow

# ── State ──────────────────────────────────────────────────────────────────────
_settings: dict = {}
_tray: tray_module.TrayIcon | None = None
_root: tk.Tk | None = None
_hotkey_mgr: hk_module.HotkeyManager | None = None
_loading_win = None


# ── Hotkey: instant feedback ───────────────────────────────────────────────────
def _on_hotkey_start(cx: int, cy: int):
    """Called immediately on hotkey press — shows loading pill before clipboard wait."""
    global _loading_win
    _loading_win = loading_module.show(_root, cx, cy)
    _tray.set_working()


# ── Hotkey: text captured, start API call ─────────────────────────────────────
def _on_hotkey(text: str, prev_hwnd: int, saved_clipboard: str | None):
    provider = _settings.get("api_provider", "openai")
    key_field = f"{provider}_api_key"
    if not _settings.get(key_field, "").strip():
        _root.after(0, lambda: (
            loading_module.dismiss(_loading_win),
            _tray.notify("API key not set — open Settings from the tray"),
            _tray.set_normal(),
        ))
        cb.restore(saved_clipboard)
        return

    def _worker():
        try:
            results = api_client.get_rephrased(text, _settings)
            _root.after(0, lambda: _finish(results, prev_hwnd, saved_clipboard))
        except api_client.APIError as e:
            msg = {
                "no_key":       "API key not set — open Settings",
                "invalid_key":  "Invalid API key — check Settings",
                "no_credits":   "No OpenAI credits — add billing at platform.openai.com/settings/billing",
                "rate_limit":   "Rate limited — try again shortly",
                "timeout":      "Request timed out",
                "bad_response": "Unexpected API response — try again",
            }.get(str(e), f"API error: {e}")
            _root.after(0, lambda m=msg: (
                loading_module.dismiss(_loading_win),
                _tray.notify(m),
                _tray.set_normal(),
            ))
            cb.restore(saved_clipboard)
        finally:
            _root.after(0, _tray.set_normal)

    threading.Thread(target=_worker, daemon=True).start()


def _finish(results: dict, prev_hwnd: int, saved_clipboard: str | None):
    loading_module.dismiss(_loading_win)
    _show_popup(results, prev_hwnd, saved_clipboard)


def _show_popup(results: dict, prev_hwnd: int, saved_clipboard: str | None):
    def _on_choice(chosen_text: str):
        replacer.simulate_replace(chosen_text, prev_hwnd, saved_clipboard)

    def _on_dismiss():
        cb.restore(saved_clipboard)

    show_popup(_root, results, _on_choice, _on_dismiss)


# ── Settings ───────────────────────────────────────────────────────────────────
def _open_settings():
    _root.after(0, _settings_window.open)


def _on_settings_saved(new_settings: dict):
    global _settings
    _settings.update(new_settings)
    _hotkey_mgr.update(_settings["hotkey"])


# ── Quit ───────────────────────────────────────────────────────────────────────
def _quit():
    _hotkey_mgr.stop()
    _tray.stop()
    _root.after(0, _root.quit)


# ── Bootstrap ──────────────────────────────────────────────────────────────────
def main():
    global _settings, _tray, _root, _hotkey_mgr, _settings_window

    _settings = cfg.load()

    # Hidden tkinter root (required for root.after() thread-safe scheduling)
    _root = tk.Tk()
    _root.withdraw()
    _root.wm_attributes("-alpha", 0)

    # System tray
    _tray = tray_module.TrayIcon(on_settings=_open_settings, on_quit=_quit)
    tray_thread = threading.Thread(target=_tray.run, daemon=True)
    tray_thread.start()

    # Settings window (lazy, reused)
    _settings_window = SettingsWindow(_root, _settings, _on_settings_saved)

    # Global hotkey
    _hotkey_mgr = hk_module.HotkeyManager(on_trigger=_on_hotkey, on_start=_on_hotkey_start)
    _hotkey_mgr.register(_settings["hotkey"])

    # If no API key is configured, open settings immediately
    provider = _settings.get("api_provider", "openai")
    if not _settings.get(f"{provider}_api_key", "").strip():
        _root.after(500, _settings_window.open)

    # Tkinter main loop (must run on main thread on Windows)
    _root.mainloop()


if __name__ == "__main__":
    main()
