"""Settings window — Obsidian redesign with dark title bar."""
import ctypes
import threading
import tkinter as tk

import keyboard as kb_lib
from . import settings as cfg

# ── Palette (matches popup) ────────────────────────────────────────────────────
BG       = "#0D0D16"
SURFACE  = "#131320"
CARD     = "#1A1A28"
HOVER    = "#1A1A2C"
BORDER   = "#22223A"
BORDER2  = "#33335A"
ACCENT   = "#6366F1"
ACCENT2  = "#4547C8"
TEXT     = "#E8E8F5"
MUTED    = "#6868A0"
DIM      = "#2E2E4A"
ENTRY_BG = "#09090F"
ERROR    = "#EF4444"

F  = "Segoe UI Variable Display"
FM = "Cascadia Code"

OPENAI_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]
CLAUDE_MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-3-5-haiku-20241022",
    "claude-sonnet-4-6",
    "claude-opus-4-6",
]


def _dark_titlebar(hwnd: int):
    """Enable dark title bar on Windows 11 via DWM."""
    try:
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)),
            ctypes.sizeof(ctypes.c_int),
        )
    except Exception:
        pass


class SettingsWindow:
    def __init__(self, root: tk.Tk, settings: dict, on_save):
        self._root = root
        self._settings = settings.copy()
        self._on_save = on_save
        self._win = None
        self._key_visible = False

    def open(self):
        if self._win and self._win.winfo_exists():
            self._win.lift()
            self._win.focus_force()
            return
        self._build()

    # ── Build ──────────────────────────────────────────────────────────────────
    def _build(self):
        win = tk.Toplevel(self._root)
        self._win = win
        win.title("Refiny — Settings")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.attributes("-topmost", True)

        # Dark title bar
        win.update_idletasks()
        _dark_titlebar(win.winfo_id())

        wrap = tk.Frame(win, bg=BG, padx=26, pady=22)
        wrap.pack(fill="both", expand=True)

        # ── Logo header ──
        hdr = tk.Frame(wrap, bg=BG)
        hdr.pack(fill="x", pady=(0, 22))
        tk.Label(hdr, text=" ◈ ", bg=ACCENT, fg="#FFF",
                 font=(F, 11, "bold")).pack(side="left")
        tk.Label(hdr, text="  Settings", bg=BG, fg=TEXT,
                 font=(F, 14, "bold")).pack(side="left")

        # ── Provider toggle ──
        _section_label(wrap, "API PROVIDER")
        self._toggle = _SegmentedToggle(
            wrap,
            options=[("OpenAI", "openai"), ("Claude", "claude")],
            initial=self._settings.get("api_provider", "openai"),
            on_change=self._on_provider,
        )
        self._toggle.pack(anchor="w", pady=(5, 18))

        # ── API Key ──
        _section_label(wrap, "API KEY")
        key_row = tk.Frame(wrap, bg=BG)
        key_row.pack(anchor="w", pady=(5, 18))

        self._key_var = tk.StringVar()
        self._key_entry = _entry(key_row, self._key_var, show="•", width=30, mono=True)
        self._key_entry.pack(side="left")

        eye = tk.Label(key_row, text="◎", bg=SURFACE, fg=MUTED,
                       font=(F, 11), padx=9, pady=5, cursor="hand2",
                       highlightthickness=1, highlightbackground=BORDER)
        eye.pack(side="left", padx=(5, 0))
        eye.bind("<Button-1>", lambda e: self._toggle_key())
        eye.bind("<Enter>", lambda e: eye.configure(fg=TEXT))
        eye.bind("<Leave>", lambda e: eye.configure(fg=MUTED))

        # ── Model ──
        _section_label(wrap, "MODEL")
        self._model_var = tk.StringVar()
        self._model_drop = _Dropdown(wrap, self._model_var, [])
        self._model_drop.pack(anchor="w", pady=(5, 18))

        # ── Hotkey ──
        _section_label(wrap, "HOTKEY")
        hk_row = tk.Frame(wrap, bg=BG)
        hk_row.pack(anchor="w", pady=(5, 0))

        self._hotkey_var = tk.StringVar(value=self._settings.get("hotkey", "ctrl+shift+r"))
        hk_e = _entry(hk_row, self._hotkey_var, state="readonly", width=18, mono=True)
        hk_e.pack(side="left")

        self._rec = tk.Label(hk_row, text="⬤  Record", bg=SURFACE, fg=MUTED,
                             font=(F, 8), padx=11, pady=6, cursor="hand2",
                             highlightthickness=1, highlightbackground=BORDER)
        self._rec.pack(side="left", padx=(6, 0))
        self._rec.bind("<Button-1>", lambda e: self._record())
        self._rec.bind("<Enter>", lambda e: self._rec.configure(fg=TEXT, highlightbackground=BORDER2))
        self._rec.bind("<Leave>", lambda e: self._rec.configure(fg=MUTED, highlightbackground=BORDER))

        # ── Divider + footer ──
        tk.Frame(wrap, bg=BORDER, height=1).pack(fill="x", pady=(22, 16))

        foot = tk.Frame(wrap, bg=BG)
        foot.pack(fill="x")

        cancel = tk.Label(foot, text="Cancel", bg=BG, fg=MUTED,
                          font=(F, 9), cursor="hand2")
        cancel.pack(side="right", padx=(10, 0))
        cancel.bind("<Button-1>", lambda e: win.destroy())
        cancel.bind("<Enter>", lambda e: cancel.configure(fg=TEXT))
        cancel.bind("<Leave>", lambda e: cancel.configure(fg=MUTED))

        save = tk.Label(foot, text="  Save Settings  ", bg=ACCENT, fg="#FFF",
                        font=(F, 9, "bold"), padx=4, pady=8, cursor="hand2")
        save.pack(side="right")
        save.bind("<Button-1>", lambda e: self._save())
        save.bind("<Enter>", lambda e: save.configure(bg=ACCENT2))
        save.bind("<Leave>", lambda e: save.configure(bg=ACCENT))

        self._populate()

        win.update_idletasks()
        win.geometry(f"430x{win.winfo_reqheight()}")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _populate(self):
        provider = self._toggle.get()
        if provider == "openai":
            self._key_var.set(self._settings.get("openai_api_key", ""))
            models, cur = OPENAI_MODELS, self._settings.get("openai_model", OPENAI_MODELS[0])
        else:
            self._key_var.set(self._settings.get("claude_api_key", ""))
            models, cur = CLAUDE_MODELS, self._settings.get("claude_model", CLAUDE_MODELS[0])
        self._model_drop.set_options(models)
        self._model_var.set(cur if cur in models else models[0])

    def _on_provider(self, val):
        prev = "openai" if val == "claude" else "claude"
        self._settings[f"{prev}_api_key"] = self._key_var.get()
        self._settings[f"{prev}_model"] = self._model_var.get()
        self._populate()

    def _toggle_key(self):
        self._key_visible = not self._key_visible
        self._key_entry.configure(show="" if self._key_visible else "•")

    def _record(self):
        self._rec.configure(text="⬤  Listening…", fg=ACCENT)
        self._win.update()

        def listen():
            try:
                combo = kb_lib.read_hotkey(suppress=False)
                self._root.after(0, lambda: self._hotkey_var.set(combo))
            except Exception:
                pass
            self._root.after(0, lambda: self._rec.configure(text="⬤  Record", fg=MUTED))

        threading.Thread(target=listen, daemon=True).start()

    def _save(self):
        p = self._toggle.get()
        key = self._key_var.get().strip()
        if not key:
            # Flash entry border red
            self._key_entry.configure(highlightbackground=ERROR, highlightcolor=ERROR)
            self._win.after(1400, lambda: self._key_entry.configure(
                highlightbackground=BORDER, highlightcolor=ACCENT))
            return
        self._settings["api_provider"] = p
        self._settings[f"{p}_api_key"] = key
        self._settings[f"{p}_model"] = self._model_var.get()
        self._settings["hotkey"] = self._hotkey_var.get()
        cfg.save(self._settings)
        self._on_save(self._settings)
        self._win.destroy()


# ── Shared widget helpers ──────────────────────────────────────────────────────

def _section_label(parent, text: str):
    tk.Label(parent, text=text, bg=BG, fg=MUTED,
             font=(F, 7, "bold")).pack(anchor="w")


def _entry(parent, var, show="", state="normal", width=28, mono=False):
    font = (FM, 9) if mono else (F, 9)
    e = tk.Entry(
        parent,
        textvariable=var,
        show=show,
        state=state,
        bg=ENTRY_BG,
        fg=TEXT,
        readonlybackground=ENTRY_BG,
        disabledbackground=ENTRY_BG,
        insertbackground=ACCENT,
        relief="flat",
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
        font=font,
        bd=5,
        width=width,
    )
    return e


class _SegmentedToggle:
    """Pill-style two-option toggle."""

    def __init__(self, parent, options, initial, on_change):
        self._var = tk.StringVar(value=initial)
        self._on_change = on_change
        self._btns = {}

        self.frame = tk.Frame(parent, bg=SURFACE,
                              highlightthickness=1, highlightbackground=BORDER)

        for label, val in options:
            active = val == initial
            btn = tk.Label(
                self.frame,
                text=label,
                bg=ACCENT if active else SURFACE,
                fg=TEXT if active else MUTED,
                font=(F, 9, "bold" if active else "normal"),
                padx=22, pady=7,
                cursor="hand2",
            )
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, v=val: self._select(v))
            self._btns[val] = btn

    def _select(self, val):
        for v, btn in self._btns.items():
            if v == val:
                btn.configure(bg=ACCENT, fg=TEXT, font=(F, 9, "bold"))
            else:
                btn.configure(bg=SURFACE, fg=MUTED, font=(F, 9, "normal"))
        self._var.set(val)
        self._on_change(val)

    def get(self):
        return self._var.get()

    def pack(self, **kw):
        self.frame.pack(**kw)


class _Dropdown:
    """Custom styled dropdown menu."""

    def __init__(self, parent, var: tk.StringVar, options: list):
        self._var = var
        self._options = options
        self._popup = None

        self._btn = tk.Label(
            parent,
            textvariable=var,
            bg=ENTRY_BG, fg=TEXT,
            font=(FM, 9),
            padx=10, pady=7,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            width=26,
            anchor="w",
        )
        self._btn.bind("<Button-1>", self._toggle)
        self._btn.bind("<Enter>", lambda e: self._btn.configure(highlightbackground=BORDER2))
        self._btn.bind("<Leave>", lambda e: self._btn.configure(highlightbackground=BORDER))

    def set_options(self, options: list):
        self._options = options
        if options and self._var.get() not in options:
            self._var.set(options[0])

    def _toggle(self, _):
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
            self._popup = None
            return
        self._open()

    def _open(self):
        self._btn.update_idletasks()
        x = self._btn.winfo_rootx()
        y = self._btn.winfo_rooty() + self._btn.winfo_height()
        w = self._btn.winfo_width()

        pop = tk.Toplevel(self._btn)
        self._popup = pop
        pop.overrideredirect(True)
        pop.attributes("-topmost", True)
        pop.configure(bg=BORDER)

        inner = tk.Frame(pop, bg=CARD, padx=1, pady=1)
        inner.pack(fill="both", expand=True)

        for opt in self._options:
            row = tk.Label(inner, text=opt, bg=CARD, fg=TEXT,
                           font=(FM, 9), padx=10, pady=7,
                           anchor="w", width=26, cursor="hand2")
            row.pack(fill="x")
            if opt == self._var.get():
                row.configure(fg=ACCENT)
            row.bind("<Enter>", lambda e, r=row: r.configure(bg=HOVER))
            row.bind("<Leave>", lambda e, r=row: r.configure(bg=CARD))
            row.bind("<Button-1>", lambda e, v=opt: self._pick(v))

        pop.geometry(f"{w}+{x}+{y}")
        pop.bind("<FocusOut>", lambda e: pop.after(100, self._close_popup))
        pop.focus_set()

    def _close_popup(self):
        if self._popup and self._popup.winfo_exists():
            try:
                if self._popup.focus_get() is None:
                    self._popup.destroy()
                    self._popup = None
            except Exception:
                pass

    def _pick(self, val):
        self._var.set(val)
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
            self._popup = None

    def pack(self, **kw):
        self._btn.pack(**kw)
