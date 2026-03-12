"""Clipboard backup, read, and restore using native Win32 API."""
import time

import win32clipboard
import win32con


def _open(retries: int = 2) -> bool:
    for _ in range(retries):
        try:
            win32clipboard.OpenClipboard()
            return True
        except Exception:
            time.sleep(0.1)
    return False


def backup() -> str | None:
    """Return current clipboard text (or None if empty/non-text)."""
    if not _open():
        return None
    try:
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            return win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        return None
    except Exception:
        return None
    finally:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass


def read() -> str:
    """Read current clipboard text."""
    if not _open():
        return ""
    try:
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            return win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT) or ""
        return ""
    except Exception:
        return ""
    finally:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass


def write(text: str) -> bool:
    """Write text to clipboard."""
    if not _open():
        return False
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        return True
    except Exception:
        return False
    finally:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass


def restore(saved: str | None) -> None:
    """Restore clipboard to previously backed-up text (or clear if None)."""
    if not _open():
        return
    try:
        win32clipboard.EmptyClipboard()
        if saved is not None:
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, saved)
    except Exception:
        pass
    finally:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass
