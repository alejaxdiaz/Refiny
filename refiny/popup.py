"""Frameless suggestion popup — Obsidian redesign."""
import tkinter as tk

import win32api

# ── Palette ────────────────────────────────────────────────────────────────────
BG      = "#0D0D16"
SURFACE = "#131320"
HOVER   = "#1A1A2C"
BORDER  = "#22223A"
ACCENT  = "#6366F1"
ACCENT2 = "#4547C8"
TEXT    = "#E8E8F5"
MUTED   = "#6868A0"
DIM     = "#2E2E4A"

C_FRIENDLY = "#10B981"
C_DIRECT   = "#F59E0B"
C_BUSINESS = "#3B82F6"

W = 460
F = "Segoe UI Variable Display"

TONES = [
    ("friendly", "FRIENDLY", C_FRIENDLY, "1"),
    ("direct",   "DIRECT",   C_DIRECT,   "2"),
    ("business", "BUSINESS", C_BUSINESS, "3"),
]


def show(root: tk.Tk, results: dict, on_choice, on_dismiss):
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    win.attributes("-alpha", 0.0)
    win.configure(bg=BORDER)

    chosen = [False]

    def pick(text):
        if chosen[0]:
            return
        chosen[0] = True
        win.destroy()
        on_choice(text)

    def dismiss(e=None):
        if chosen[0]:
            return
        chosen[0] = True
        win.destroy()
        on_dismiss()

    # ── Shell (1px border) ──
    shell = tk.Frame(win, bg=BORDER, padx=1, pady=1)
    shell.pack(fill="both", expand=True)

    body = tk.Frame(shell, bg=BG)
    body.pack(fill="both", expand=True)

    # ── Header ──
    hdr = tk.Frame(body, bg=BG, padx=14, pady=10)
    hdr.pack(fill="x")

    badge = tk.Frame(hdr, bg=BG)
    badge.pack(side="left")
    tk.Label(badge, text=" ◈ ", bg=ACCENT, fg="#FFF",
             font=(F, 9, "bold")).pack(side="left")
    tk.Label(badge, text="  Refiny", bg=BG, fg=TEXT,
             font=(F, 9, "bold")).pack(side="left")

    tk.Label(hdr, text="1 · 2 · 3  ·  esc", bg=BG, fg=DIM,
             font=(F, 7)).pack(side="right")

    # ── Divider ──
    tk.Frame(body, bg=BORDER, height=1).pack(fill="x")

    # ── Cards ──
    cards = tk.Frame(body, bg=BG, pady=8)
    cards.pack(fill="both", expand=True)

    for key, label, color, sc in TONES:
        _card(cards, label, color, sc, results.get(key, "—"), pick)

    # ── Size + position ──
    win.update_idletasks()
    rh = win.winfo_reqheight()
    cx, cy = win32api.GetCursorPos()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    px = max(0, min(cx + 14, sw - W - 8))
    ty = max(0, min(cy + 14, sh - rh - 8))

    win.geometry(f"{W}x{rh}+{px}+{ty + 18}")

    # ── Animate in ──
    _animate(win, ty + 18, ty, W, rh)

    # ── Bindings ──
    win.bind("<Escape>", dismiss)
    for i, (key, _, _, _) in enumerate(TONES, 1):
        win.bind(str(i), lambda e, k=key: pick(results.get(k, "")))
    win.bind("<FocusOut>", lambda e: win.after(130, lambda: _focusout(win, chosen, dismiss)))
    win.focus_force()


def _card(parent, label, color, shortcut, text, pick_fn):
    wrap = tk.Frame(parent, bg=BG)
    wrap.pack(fill="x", padx=10, pady=2)

    card = tk.Frame(wrap, bg=SURFACE)
    card.pack(fill="x")

    # Left accent bar
    bar = tk.Frame(card, bg=color, width=3)
    bar.pack(side="left", fill="y")

    # Main content
    cnt = tk.Frame(card, bg=SURFACE, padx=12, pady=9)
    cnt.pack(side="left", fill="both", expand=True)

    top_row = tk.Frame(cnt, bg=SURFACE)
    top_row.pack(fill="x")
    lbl = tk.Label(top_row, text=label, bg=SURFACE, fg=color,
                   font=(F, 7, "bold"))
    lbl.pack(side="left")
    sc_lbl = tk.Label(top_row, text=f"  [{shortcut}]", bg=SURFACE, fg=DIM,
                      font=(F, 7))
    sc_lbl.pack(side="left")

    body_lbl = tk.Label(cnt, text=text, bg=SURFACE, fg=TEXT,
                        font=(F, 9), wraplength=W - 130,
                        justify="left", anchor="w")
    body_lbl.pack(fill="x", pady=(3, 0))

    # Use button (right-side, vertically centred)
    btn_wrap = tk.Frame(card, bg=SURFACE, padx=12)
    btn_wrap.pack(side="right", fill="y")
    btn = tk.Label(btn_wrap, text="Use →", bg=ACCENT, fg="#FFF",
                   font=(F, 8, "bold"), padx=10, pady=5, cursor="hand2")
    btn.pack(expand=True)

    # Hover — all bg to HOVER, bar stays colored, btn dims
    surf_widgets = [wrap, card, cnt, top_row, lbl, sc_lbl, body_lbl, btn_wrap]

    def enter(_):
        for w in surf_widgets:
            try:
                w.configure(bg=HOVER)
            except Exception:
                pass
        bar.configure(bg=color)
        btn.configure(bg=ACCENT2)

    def leave(_):
        for w in surf_widgets:
            try:
                w.configure(bg=SURFACE)
            except Exception:
                pass
        bar.configure(bg=color)
        btn.configure(bg=ACCENT)

    for w in surf_widgets + [bar, btn]:
        w.bind("<Enter>", enter)
        w.bind("<Leave>", leave)
        w.bind("<Button-1>", lambda e, t=text: pick_fn(t))


def _animate(win, start_y, target_y, w, h):
    steps, interval = 9, 14

    def step(i):
        if not win.winfo_exists():
            return
        if i >= steps:
            win.geometry(f"{w}x{h}+{win.winfo_x()}+{target_y}")
            win.attributes("-alpha", 0.97)
            return
        t = (i + 1) / steps
        ease = 1 - (1 - t) ** 2
        y = int(start_y + (target_y - start_y) * ease)
        win.geometry(f"+{win.winfo_x()}+{y}")
        win.attributes("-alpha", round(0.97 * ease, 2))
        win.after(interval, lambda: step(i + 1))

    step(0)


def _focusout(win, chosen, dismiss):
    try:
        if win.winfo_exists() and win.focus_get() is None and not chosen[0]:
            dismiss()
    except Exception:
        pass
