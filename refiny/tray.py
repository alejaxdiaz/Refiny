"""System tray icon management using pystray."""
import pathlib
import sys

from PIL import Image, ImageDraw
import pystray


def _resource(name: str) -> pathlib.Path:
    base = pathlib.Path(getattr(sys, "_MEIPASS", pathlib.Path(__file__).parent.parent))
    return base / "assets" / name


def _make_icon(color: str) -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Draw rounded background circle
    d.ellipse([4, 4, size - 4, size - 4], fill=color)
    # Draw "R" letter
    d.text((20, 14), "R", fill="#FFFFFF")
    return img


def _load_icon(name: str, fallback_color: str) -> Image.Image:
    path = _resource(name)
    if path.exists():
        return Image.open(path).convert("RGBA")
    return _make_icon(fallback_color)


class TrayIcon:
    def __init__(self, on_settings, on_quit):
        self._on_settings = on_settings
        self._on_quit = on_quit
        self._icon: pystray.Icon | None = None
        self._img_normal = _load_icon("icon.png", "#7C6AF7")
        self._img_working = _load_icon("icon_gray.png", "#666688")

    def run(self):
        menu = pystray.Menu(
            pystray.MenuItem("Settings", self._open_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit Refiny", self._quit),
        )
        self._icon = pystray.Icon(
            "Refiny",
            self._img_normal,
            "Refiny  ·  Ctrl+Shift+R",
            menu,
        )
        self._icon.run()

    def set_working(self):
        if self._icon:
            self._icon.icon = self._img_working
            self._icon.title = "Refiny  ·  Working…"

    def set_normal(self):
        if self._icon:
            self._icon.icon = self._img_normal
            self._icon.title = "Refiny  ·  Ctrl+Shift+R"

    def notify(self, message: str):
        if self._icon:
            try:
                self._icon.notify(message, "Refiny")
            except Exception:
                pass

    def stop(self):
        if self._icon:
            self._icon.stop()

    def _open_settings(self, icon, item):
        self._on_settings()

    def _quit(self, icon, item):
        self._on_quit()
