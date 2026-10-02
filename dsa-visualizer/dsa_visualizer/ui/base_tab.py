"""BaseTab: layout, transport bar (play / pause / step / scrub) and GIF export."""

import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ..colors import AMBER, BG, BORDER, CYAN, DIM, MUTED, PANEL
from .theme import F
from .widgets import Board, InfoCard, PseudoPanel, label, make_entry


class BaseTab(tk.Frame):
    NAME = ""

    def __init__(self, app):
        super().__init__(app.notebook, bg=BG)
        self.app = app
        self.frames, self.idx = [], 0
        self.playing = False
        self._job = None
        self._lock = False
        self.legend = []
        self.note = ""

        side = tk.Frame(
            self, bg=PANEL, width=284, highlightbackground=BORDER, highlightthickness=1
        )
        side.pack(side="left", fill="y", padx=(0, 12))
        side.pack_propagate(False)
        inner = tk.Frame(side, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=14, pady=14)

        self.right = tk.Frame(self, bg=BG)
        self.right.pack(side="left", fill="both", expand=True)
        self.board = Board(self.right, self.refresh)
        self.board.pack(fill="both", expand=True)
        self._build_transport()
        bottom = tk.Frame(self.right, bg=BG)
        bottom.pack(fill="x", pady=(10, 0))
        self.pseudo = PseudoPanel(bottom)
        self.pseudo.pack(side="left", fill="both", expand=True)
        self.info = InfoCard(bottom)
        self.info.pack(side="left", fill="y", padx=(10, 0))

        self.build_controls(inner)
        self.after(300, lambda: self.start(autoplay=False))

    # ---- control-panel helpers ----
    def section(self, parent, text):
        label(parent, text, 8, "bold", fg=DIM).pack(anchor="w", pady=(10, 3))

    def combo(self, parent, values, default=0):
        c = ttk.Combobox(parent, state="readonly", values=values, font=F(10))
        c.current(default)
        c.pack(fill="x")
        c.bind("<<ComboboxSelected>>", self._on_pick)
        return c

    def _on_pick(self, _e):
        self.board.focus_set()
        self.start(autoplay=False)

    def button(self, parent, text, cmd, accent=False):
        b = ttk.Button(
            parent,
            text=text,
            command=cmd,
            takefocus=0,
            style="Accent.TButton" if accent else "TButton",
        )
        b.pack(fill="x", pady=3)
        return b

    def entry(self, parent, text):
        e = make_entry(parent, text)
        e.pack(fill="x", ipady=5)
        return e

    # ---- transport bar ----
    def _build_transport(self):
        bar = tk.Frame(
            self.right, bg=PANEL, highlightbackground=BORDER, highlightthickness=1
        )
        bar.pack(fill="x", pady=(10, 0))
        row = tk.Frame(bar, bg=PANEL)
        row.pack(fill="x", padx=10, pady=7)

        def btn(text, cmd, style="Tool.TButton"):
            b = ttk.Button(
                row, text=text, command=cmd, style=style, takefocus=0, width=7
            )
            b.pack(side="left", padx=(0, 5))
            return b

        btn("|<", self.first)
        btn("< Step", lambda: self.step(-1))
        self.play_btn = btn("Play", self.toggle, "Play.TButton")
        btn("Step >", lambda: self.step(1))
        btn(">|", self.last)
        btn("Replay", self.replay)
        self.scrub = tk.Scale(
            row,
            from_=0,
            to=1,
            orient="horizontal",
            showvalue=0,
            resolution=1,
            bg=PANEL,
            troughcolor=BORDER,
            activebackground=CYAN,
            highlightthickness=0,
            bd=0,
            sliderrelief="flat",
            sliderlength=16,
            width=10,
            takefocus=0,
            command=self._on_scrub,
        )
        self.scrub.pack(side="left", fill="x", expand=True, padx=8)
        self.step_lbl = label(
            row, "Step 0 / 0", 9, fg=MUTED, bg=PANEL, mono=True, width=13
        )
        self.step_lbl.pack(side="left")
        label(row, "Speed", 9, fg=DIM, bg=PANEL).pack(side="left", padx=(8, 2))
        tk.Scale(
            row,
            from_=1,
            to=10,
            orient="horizontal",
            showvalue=0,
            variable=self.app.speed,
            bg=PANEL,
            troughcolor=BORDER,
            activebackground=AMBER,
            highlightthickness=0,
            bd=0,
            sliderrelief="flat",
            sliderlength=14,
            width=10,
            length=90,
            takefocus=0,
        ).pack(side="left")

    def delay(self):
        return max(20, int(1000 * 0.72 ** (self.app.speed.get() - 1)))

    # ---- playback engine ----
    def load(self, frames, autoplay=True):
        self.pause()
        self.frames = frames
        self.scrub.config(to=max(1, len(frames) - 1))
        self.show(0)
        if autoplay:
            self.play()

    def show(self, i, from_scrub=False):
        if not self.frames:
            return
        self.idx = max(0, min(int(i), len(self.frames) - 1))
        self.render(self.frames[self.idx])
        self.step_lbl.config(text=f"Step {self.idx + 1} / {len(self.frames)}")
        if not from_scrub:
            self._lock = True
            self.scrub.set(self.idx)
            self._lock = False

    def refresh(self):
        if self.frames:
            self.render(self.frames[self.idx])

    def _on_scrub(self, v):
        if self._lock or not self.frames:
            return
        i = int(round(float(v)))
        if i != self.idx:
            self.pause()
            self.show(i, from_scrub=True)

    def play(self):
        if not self.frames:
            return
        if self.idx >= len(self.frames) - 1:
            self.show(0)
        self.playing = True
        self.play_btn.config(text="Pause")
        self._job = self.after(self.delay(), self._tick)

    def _tick(self):
        self._job = None
        if not self.playing:
            return
        self.show(self.idx + 1)
        if self.idx >= len(self.frames) - 1:
            self.pause()
            return
        self._job = self.after(self.delay(), self._tick)

    def pause(self):
        if self._job:
            self.after_cancel(self._job)
            self._job = None
        self.playing = False
        self.play_btn.config(text="Play")

    def toggle(self):
        self.pause() if self.playing else self.play()

    def step(self, d):
        self.pause()
        self.show(self.idx + d)

    def first(self):
        self.pause()
        self.show(0)

    def last(self):
        self.pause()
        self.show(len(self.frames) - 1)

    def replay(self):
        self.pause()
        self.show(0)
        self.play()

    # ---- GIF export (screen-captures the visualisation area) ----
    def export_gif(self):
        if not self.frames:
            return
        try:
            from PIL import Image, ImageGrab
        except ImportError:
            messagebox.showinfo(
                "Export GIF", "GIF export needs Pillow.\n\nRun:  pip install pillow"
            )
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF image", "*.gif")],
            initialfile="visualization.gif",
        )
        if not path:
            return
        self.pause()
        keep = self.idx
        stride = max(1, math.ceil(len(self.frames) / 150))
        picks = list(range(0, len(self.frames), stride))
        if picks[-1] != len(self.frames) - 1:
            picks.append(len(self.frames) - 1)
        images = []
        try:
            for n, i in enumerate(picks):
                self.info.status.config(text=f"Exporting GIF... {n + 1}/{len(picks)}")
                self.show(i)
                self.update_idletasks()
                self.update()
                x, y = self.right.winfo_rootx(), self.right.winfo_rooty()
                w, h = self.right.winfo_width(), self.right.winfo_height()
                img = ImageGrab.grab(bbox=(x, y, x + w, y + h)).convert("RGB")
                if img.width > 1000:
                    img = img.resize((1000, int(img.height * 1000 / img.width)))
                images.append(img.convert("P", palette=Image.ADAPTIVE))
            durations = [self.delay()] * (len(images) - 1) + [1500]
            images[0].save(
                path,
                save_all=True,
                append_images=images[1:],
                duration=durations,
                loop=0,
            )
            messagebox.showinfo("Export GIF", f"Saved {len(images)} frames to\n{path}")
        except Exception as exc:  # screen capture can fail on some systems
            messagebox.showerror("Export GIF", f"Could not export:\n{exc}")
        finally:
            self.show(keep)

    # ---- to be provided by subclasses ----
    def build_controls(self, parent):
        raise NotImplementedError

    def start(self, autoplay=True):
        raise NotImplementedError

    def render(self, frame):
        raise NotImplementedError
