"""Replace selected text by returning focus to the original window and pasting."""
import threading
import time

import win32gui
from pynput.keyboard import Controller, Key

_kb = Controller()


def simulate_replace(new_text: str, prev_hwnd: int, original_clipboard: str | None) -> None:
    """Paste new_text into the original window, replacing the selection."""
    from . import clipboard as cb

    # Write new text to clipboard
    cb.write(new_text)

    # Return focus to original window
    try:
        if prev_hwnd and win32gui.IsWindow(prev_hwnd):
            win32gui.SetForegroundWindow(prev_hwnd)
            time.sleep(0.06)
    except Exception:
        pass

    # Paste (replaces active selection)
    _kb.press(Key.ctrl)
    _kb.press("v")
    _kb.release("v")
    _kb.release(Key.ctrl)

    # Restore original clipboard after paste completes
    def _restore():
        time.sleep(0.5)
        cb.restore(original_clipboard)

    threading.Thread(target=_restore, daemon=True).start()
