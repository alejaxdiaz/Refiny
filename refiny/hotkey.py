"""Global hotkey registration and selected-text capture."""
import time

import keyboard
import win32gui
from pynput.keyboard import Controller, Key

_kb = Controller()


class HotkeyManager:
    def __init__(self, on_trigger, on_start=None):
        """
        on_start(cx, cy)  — fired immediately on hotkey press (before clipboard wait).
        on_trigger(text, prev_hwnd, saved) — fired once selected text is captured.
        """
        self._on_trigger = on_trigger
        self._on_start = on_start
        self._hotkey = None

    def register(self, combo: str):
        self._unregister()
        try:
            keyboard.add_hotkey(combo, self._handle, suppress=True)
            self._hotkey = combo
        except Exception:
            pass

    def _unregister(self):
        if self._hotkey:
            try:
                keyboard.remove_hotkey(self._hotkey)
            except Exception:
                pass
            self._hotkey = None

    def update(self, new_combo: str):
        self.register(new_combo)

    def stop(self):
        self._unregister()

    def _handle(self):
        from . import clipboard as cb
        import win32api

        # Capture context immediately, before anything else
        prev_hwnd = win32gui.GetForegroundWindow()
        cx, cy = win32api.GetCursorPos()

        # Signal UI immediately so user sees feedback right away
        if self._on_start:
            self._on_start(cx, cy)

        # Backup clipboard then simulate Ctrl+C
        saved = cb.backup()
        _kb.press(Key.ctrl)
        _kb.press("c")
        _kb.release("c")
        _kb.release(Key.ctrl)

        # Reduced from 150ms — 80ms is sufficient for most apps
        time.sleep(0.08)

        selected = cb.read()

        if not selected.strip():
            cb.restore(saved)
            return

        self._on_trigger(selected.strip(), prev_hwnd, saved)
