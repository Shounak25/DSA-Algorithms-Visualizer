"""Main application window: header, notebook of tabs, styles, shortcuts."""

import tkinter as tk
from tkinter import ttk

from .colors import (
    BG,
    BORDER,
    CYAN,
    DIM,
    GREEN,
    INDIGO,
    MUTED,
    PANEL,
    PANEL_2,
    PINK,
    TEXT,
    gradient,
)
from .ui.graph_tab import GraphTab
from .ui.sort_tab import SortTab
from .ui.theme import F, init_fonts
from .ui.tree_tab import TreeTab


class DSAVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        init_fonts(self)
        self.title("DSA Visualizer")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{min(1320, sw - 40)}x{min(860, sh - 90)}+20+20")
        self.minsize(1040, 640)
        self.configure(bg=BG)
        self.speed = tk.DoubleVar(value=5)

        self._style()
        self._header()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        self.tabs = [TreeTab(self), GraphTab(self), SortTab(self)]
        for t in self.tabs:
            self.notebook.add(t, text=t.NAME, padding=(0, 12, 0, 0))
        self.notebook.bind(
            "<<NotebookTabChanged>>", lambda e: [t.pause() for t in self.tabs]
        )
        for key, action in (
            ("<space>", "toggle"),
            ("<Left>", "back"),
            ("<Right>", "forward"),
            ("<Home>", "first"),
            ("<End>", "last"),
        ):
            self.bind_all(key, lambda e, a=action: self._shortcut(a))

    def _shortcut(self, action):
        if isinstance(self.focus_get(), (tk.Entry, ttk.Entry, ttk.Combobox)):
            return None
        tab = self.nametowidget(self.notebook.select())
        {
            "toggle": tab.toggle,
            "back": lambda: tab.step(-1),
            "forward": lambda: tab.step(1),
            "first": tab.first,
            "last": tab.last,
        }[action]()
        return "break"

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(
            ".",
            background=PANEL,
            foreground=TEXT,
            font=F(10),
            bordercolor=BORDER,
            focuscolor=PANEL,
        )
        s.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(0, 0, 0, 0))
        s.configure(
            "TNotebook.Tab",
            background=PANEL,
            foreground=MUTED,
            padding=(22, 10),
            font=F(10, "bold"),
            borderwidth=0,
        )
        s.map(
            "TNotebook.Tab",
            background=[("selected", INDIGO), ("active", PANEL_2)],
            foreground=[("selected", "#ffffff"), ("active", TEXT)],
            expand=[("selected", (0, 0, 0, 0))],
        )
        s.configure("TFrame", background=BG)
        s.configure(
            "TButton",
            background=PANEL_2,
            foreground=TEXT,
            padding=(12, 8),
            borderwidth=0,
            focusthickness=0,
            font=F(10, "bold"),
        )
        s.map(
            "TButton",
            background=[("pressed", INDIGO), ("active", BORDER)],
            foreground=[("disabled", DIM)],
        )
        s.configure(
            "Accent.TButton", background=INDIGO, foreground="#ffffff", padding=(12, 9)
        )
        s.map(
            "Accent.TButton", background=[("pressed", "#4f46e5"), ("active", "#7c7ff5")]
        )
        s.configure("Tool.TButton", padding=(10, 6), font=F(9, "bold"))
        s.configure(
            "Play.TButton",
            background=GREEN,
            foreground="#04130d",
            padding=(14, 6),
            font=F(9, "bold"),
        )
        s.map(
            "Play.TButton", background=[("pressed", "#10b981"), ("active", "#6ee7b7")]
        )
        s.configure(
            "TCombobox",
            fieldbackground=PANEL_2,
            background=PANEL_2,
            foreground=TEXT,
            arrowcolor=CYAN,
            bordercolor=BORDER,
            lightcolor=PANEL_2,
            darkcolor=PANEL_2,
            padding=6,
            selectbackground=PANEL_2,
            selectforeground=TEXT,
        )
        s.map(
            "TCombobox",
            fieldbackground=[("readonly", PANEL_2), ("disabled", PANEL)],
            foreground=[("disabled", DIM)],
            background=[("active", PANEL_2)],
        )
        s.configure("Panel.TCheckbutton", background=PANEL, foreground=TEXT, font=F(10))
        s.map(
            "Panel.TCheckbutton",
            background=[("active", PANEL)],
            indicatorcolor=[("selected", CYAN), ("!selected", PANEL_2)],
        )
        self.option_add("*TCombobox*Listbox.background", PANEL_2)
        self.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.option_add("*TCombobox*Listbox.selectBackground", INDIGO)
        self.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
        self.option_add("*TCombobox*Listbox.font", F(10))

    def _header(self):
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=22, pady=(14, 8))
        left = tk.Frame(head, bg=BG)
        left.pack(side="left")
        tk.Label(left, text="DSA Visualizer", font=F(21, "bold"), fg=TEXT, bg=BG).pack(
            anchor="w"
        )
        tk.Label(
            left,
            text="Trees, graphs and sorting, one step at a time",
            font=F(10),
            fg=MUTED,
            bg=BG,
        ).pack(anchor="w")
        tk.Label(
            head,
            text="Space  play/pause     Left / Right  step     " "Home / End  jump",
            font=F(9),
            fg=DIM,
            bg=BG,
        ).pack(side="right", anchor="s")
        bar = tk.Canvas(self, height=3, bg=BG, highlightthickness=0)
        bar.pack(fill="x", padx=22, pady=(0, 10))

        def paint(_e=None):
            bar.delete("all")
            w = max(bar.winfo_width(), 2)
            for x in range(0, w, 2):
                bar.create_line(
                    x, 0, x, 3, width=2, fill=gradient([INDIGO, CYAN, PINK], x / w)
                )

        bar.bind("<Configure>", paint)


def main():
    """Launch the application."""
    DSAVisualizer().mainloop()
