"""Reusable Tk widgets: canvas board, pseudocode panel and status card."""

import re
import tkinter as tk

from ..colors import (
    BORDER,
    CANVAS,
    CODE_BG,
    CYAN,
    DIM,
    GRID,
    INDIGO,
    MUTED,
    PANEL,
    PANEL_2,
    PURPLE,
    TEXT,
    mix,
)
from .theme import F, M


def label(
    parent, text="", size=10, weight="normal", fg=TEXT, bg=PANEL, mono=False, **kw
):
    font = M(size, weight) if mono else F(size, weight)
    return tk.Label(
        parent, text=text, font=font, fg=fg, bg=bg, anchor="w", justify="left", **kw
    )


def make_entry(parent, text):
    e = tk.Entry(
        parent,
        bg=PANEL_2,
        fg=TEXT,
        insertbackground=CYAN,
        relief="flat",
        font=M(10),
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=CYAN,
        selectbackground=INDIGO,
        selectforeground="#ffffff",
    )
    e.insert(0, text)
    return e


def set_entry(entry, text):
    entry.delete(0, "end")
    entry.insert(0, text)


class Board(tk.Canvas):
    def __init__(self, parent, on_resize):
        super().__init__(
            parent,
            bg=CANVAS,
            highlightthickness=1,
            highlightbackground=BORDER,
            takefocus=0,
        )
        self.on_resize = on_resize
        self._job = None
        self.bind("<Configure>", self._configure)

    @property
    def W(self):
        return max(self.winfo_width(), 400)

    @property
    def H(self):
        return max(self.winfo_height(), 260)

    def _configure(self, _event):
        if self._job:
            self.after_cancel(self._job)
        self._job = self.after(40, self._apply)

    def _apply(self):
        self._job = None
        self.draw_grid()
        self.on_resize()

    def draw_grid(self):
        self.delete("bg")
        w, h = self.winfo_width(), self.winfo_height()
        for x in range(16, w, 32):
            for y in range(16, h, 32):
                self.create_rectangle(
                    x, y, x + 2, y + 2, fill=GRID, outline="", tags="bg"
                )
        try:
            self.tag_lower("bg")
        except tk.TclError:
            pass

    def clear(self):
        self.delete("dyn")

    # ---- primitives (everything animated is tagged "dyn") ----
    def circle(self, x, y, r, fill, outline, width=2, halo=None):
        if halo:
            for dr, t in ((11, 0.82), (6, 0.58)):
                self.create_oval(
                    x - r - dr,
                    y - r - dr,
                    x + r + dr,
                    y + r + dr,
                    outline=mix(halo, CANVAS, t),
                    width=2,
                    tags="dyn",
                )
        self.create_oval(
            x - r,
            y - r,
            x + r,
            y + r,
            fill=fill,
            outline=outline,
            width=width,
            tags="dyn",
        )

    def rrect(self, x1, y1, x2, y2, r, **kw):
        r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
        pts = [
            x1 + r,
            y1,
            x2 - r,
            y1,
            x2,
            y1,
            x2,
            y1 + r,
            x2,
            y2 - r,
            x2,
            y2,
            x2 - r,
            y2,
            x1 + r,
            y2,
            x1,
            y2,
            x1,
            y2 - r,
            x1,
            y1 + r,
            x1,
            y1,
        ]
        return self.create_polygon(pts, smooth=True, tags="dyn", **kw)

    def txt(
        self,
        x,
        y,
        text,
        fill=TEXT,
        size=10,
        weight="normal",
        anchor="center",
        mono=False,
    ):
        font = M(size, weight) if mono else F(size, weight)
        return self.create_text(
            x, y, text=text, fill=fill, font=font, anchor=anchor, tags="dyn"
        )

    def pill(self, x, y, text, fg=MUTED, fill=CANVAS, outline=BORDER, size=9):
        t = self.txt(x, y, text, fg, size, "bold", mono=True)
        x1, y1, x2, y2 = self.bbox(t)
        box = self.rrect(x1 - 6, y1 - 2, x2 + 6, y2 + 2, 7, fill=fill, outline=outline)
        self.tag_lower(box, t)
        return t

    def legend(self, items, x, y):
        for text, color in items:
            self.create_oval(
                x, y - 5, x + 10, y + 5, fill=color, outline="", tags="dyn"
            )
            t = self.txt(x + 16, y, text, MUTED, 9, anchor="w")
            x = self.bbox(t)[2] + 18


# --------------------------------------------------------------------------
# Pseudocode panel with a moving highlight
# --------------------------------------------------------------------------
KEYWORDS = re.compile(
    r"\b(for|while|if|else|return|break|continue|and|or|not|to|downto|"
    r"swap|visit|push|pop|each|is|in)\b"
)


class CodeView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CODE_BG)
        self.title = tk.Label(
            self, text="", font=F(8, "bold"), fg=DIM, bg=CODE_BG, anchor="w"
        )
        self.title.pack(fill="x", padx=12, pady=(8, 0))
        self.text = tk.Text(
            self,
            height=10,
            width=20,
            wrap="none",
            bg=CODE_BG,
            fg=MUTED,
            font=M(10),
            relief="flat",
            padx=8,
            pady=4,
            highlightthickness=0,
            cursor="arrow",
            state="disabled",
            takefocus=0,
            spacing1=1,
            spacing3=1,
            borderwidth=0,
        )
        self.text.pack(fill="both", expand=True)
        self.text.tag_configure("num", foreground=DIM)
        self.text.tag_configure("kw", foreground=PURPLE)
        self.text.tag_configure("cm", foreground=DIM)
        self.text.tag_configure(
            "hl", background=mix(INDIGO, CODE_BG, 0.45), foreground="#ffffff"
        )
        self.lines = []

    def set_code(self, title, lines):
        self.lines = lines
        self.title.config(text="PSEUDOCODE  -  " + title.upper())
        t = self.text
        t.config(state="normal")
        t.delete("1.0", "end")
        for i, line in enumerate(lines):
            t.insert("end", f"{i + 1:>2}  {line}\n")
            row = i + 1
            t.tag_add("num", f"{row}.0", f"{row}.4")
            for m in KEYWORDS.finditer(line):
                t.tag_add("kw", f"{row}.{4 + m.start()}", f"{row}.{4 + m.end()}")
            c = line.find("#")
            if c >= 0:
                t.tag_add("cm", f"{row}.{4 + c}", f"{row}.end")
        t.tag_raise("hl")
        t.config(state="disabled")

    def highlight(self, i):
        t = self.text
        t.tag_remove("hl", "1.0", "end")
        if i is None or i < 0 or i >= len(self.lines):
            return
        t.tag_add("hl", f"{i + 1}.0", f"{i + 1}.end+1c")
        t.see(f"{i + 1}.0")


class PseudoPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(
            parent, bg=CODE_BG, highlightbackground=BORDER, highlightthickness=1
        )
        self.views = [CodeView(self), CodeView(self)]
        self.active = 1

    def show(self, *codes):
        for v in self.views:
            v.pack_forget()
        self.active = len(codes)
        for v, (title, lines) in zip(self.views, codes):
            v.set_code(title, lines)
            v.pack(side="left", fill="both", expand=True)

    def highlight(self, *idx):
        for v, i in zip(self.views[: self.active], idx):
            v.highlight(i)


# --------------------------------------------------------------------------
# Status card
# --------------------------------------------------------------------------
class InfoCard(tk.Frame):
    def __init__(self, parent):
        super().__init__(
            parent,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
            width=350,
        )
        self.pack_propagate(False)
        inner = tk.Frame(self, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=14, pady=10)
        label(inner, "STATUS", 8, "bold", fg=DIM).pack(anchor="w")
        self.status = label(inner, "Ready", 11, "bold", wraplength=320)
        self.status.pack(anchor="w", fill="x", pady=(2, 4))
        self.result = label(inner, "", 9, fg=CYAN, mono=True, wraplength=320)
        self.result.pack(anchor="w", fill="x")
        self.stats = label(inner, "", 9, fg=MUTED, mono=True, wraplength=320)
        self.stats.pack(anchor="w", fill="x", pady=(4, 0))
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=8)
        self.note = label(inner, "", 9, fg=DIM, wraplength=320)
        self.note.pack(anchor="w", fill="x")

    def set(self, status, result="", stats="", note="", color=TEXT):
        self.status.config(text=status, fg=color)
        self.result.config(text=result)
        self.stats.config(text=stats)
        self.note.config(text=note)
