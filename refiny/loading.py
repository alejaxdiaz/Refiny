"""Instant loading indicator — appears near cursor while API call runs."""
import tkinter as tk

BG     = "#0D0D16"
BORDER = "#22223A"
ACCENT = "#6366F1"
TEXT   = "#E8E8F5"
DIM    = "#44446A"
F      = "Segoe UI Variable Display"

DOTS = ["   ", ".  ", ".. ", "..."]


def show(root: tk.Tk, cx: int, cy: int):
    """Show loading popup near (cx, cy). Returns the Toplevel window."""
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    win.attributes("-alpha", 0.0)
    win.configure(bg=BORDER)

    shell = tk.Frame(win, bg=BORDER, padx=1, pady=1)
    shell.pack(fill="both", expand=True)
    body = tk.Frame(shell, bg=BG, padx=14, pady=9)
    body.pack(fill="both", expand=True)

    row = tk.Frame(body, bg=BG)
    row.pack()

    tk.Label(row, text=" ◈ ", bg=ACCENT, fg="#FFF",
             font=(F, 8, "bold")).pack(side="left")
    tk.Label(row, text=" Refiny", bg=BG, fg=TEXT,
             font=(F, 9, "bold")).pack(side="left")

    dot_var = tk.StringVar(value=DOTS[0])
    tk.Label(row, textvariable=dot_var, bg=BG, fg=DIM,
             font=("Cascadia Code", 9), width=3).pack(side="left")

    # Position near cursor
    win.update_idletasks()
    w = win.winfo_reqwidth()
    h = win.winfo_reqheight()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    px = max(0, min(cx + 14, sw - w - 8))
    py = max(0, min(cy + 14, sh - h - 8))
    win.geometry(f"{w}x{h}+{px}+{py}")

    # Fade in over ~80ms
    def _fade(step=0):
        if not win.winfo_exists():
            return
        a = min(0.93, step * 0.16)
        win.attributes("-alpha", a)
        if a < 0.93:
            win.after(14, lambda: _fade(step + 1))

    _fade()

    # Dot animation
    idx = [0]

    def _tick():
        if not win.winfo_exists():
            return
        idx[0] = (idx[0] + 1) % len(DOTS)
        dot_var.set(DOTS[idx[0]])
        win.after(380, _tick)

    _tick()
    return win


def dismiss(win):
    try:
        if win and win.winfo_exists():
            win.destroy()
    except Exception:
        pass
