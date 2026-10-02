"""Sorting tab: six algorithms plus a side-by-side race mode."""

import random
import tkinter as tk
from tkinter import ttk

from ..algorithms.complexity import COMPLEXITY
from ..algorithms.pseudocode import PSEUDO_SORT
from ..algorithms.sorting import SORTS, race_frames
from ..colors import (
    AMBER,
    BORDER,
    CANVAS,
    DIM,
    GREEN,
    INDIGO,
    MUTED,
    PANEL,
    PURPLE,
    RED,
    TEXT,
    gradient,
    mix,
)
from .base_tab import BaseTab
from .theme import F
from .widgets import label, set_entry

BAR_GRADIENT = ["#38bdf8", "#818cf8", "#e879f9"]


class SortTab(BaseTab):
    NAME = "  Sorting  "

    def build_controls(self, p):
        self.race = tk.BooleanVar(value=False)
        self.name_a = self.name_b = ""
        label(p, "Sorting", 14, "bold").pack(anchor="w")
        label(
            p,
            "Watch every comparison and swap, or race two algorithms "
            "on the same array.",
            9,
            fg=MUTED,
            wraplength=250,
        ).pack(anchor="w", pady=(2, 6))
        self.section(p, "ALGORITHM")
        self.algo = self.combo(p, list(SORTS))
        self.section(p, "ARRAY  (comma-separated, up to 40)")
        self.array = self.entry(
            p, ", ".join(str(random.randint(10, 99)) for _ in range(14))
        )
        tk.Frame(p, bg=PANEL, height=6).pack()
        ttk.Checkbutton(
            p,
            text="Race mode (two algorithms)",
            variable=self.race,
            command=self._race_toggle,
            style="Panel.TCheckbutton",
            takefocus=0,
        ).pack(anchor="w", pady=(6, 3))
        self.algo_b = ttk.Combobox(p, state="disabled", values=list(SORTS), font=F(10))
        self.algo_b.current(3)
        self.algo_b.pack(fill="x")
        self.algo_b.bind("<<ComboboxSelected>>", self._on_pick)
        tk.Frame(p, bg=PANEL, height=8).pack()
        self.button(p, "Visualize", lambda: self.start(True), accent=True)
        self.button(p, "Shuffle & replay", self.shuffle_replay)
        self.button(p, "New array", self.new_array)
        self.button(p, "Export GIF", self.export_gif)

    def _race_toggle(self):
        self.algo_b.config(state="readonly" if self.race.get() else "disabled")
        self.start(False)

    def _random_values(self, n):
        return ", ".join(str(random.randint(10, 99)) for _ in range(n))

    def new_array(self):
        set_entry(self.array, self._random_values(14))
        self.start(False)

    def shuffle_replay(self):
        try:
            n = len([x for x in self.array.get().split(",") if x.strip()])
        except Exception:
            n = 14
        set_entry(self.array, self._random_values(min(40, max(2, n))))
        self.start(True)

    def start(self, autoplay=True):
        self.pause()
        try:
            values = [int(x) for x in self.array.get().split(",") if x.strip()]
            if not values or len(values) > 40:
                raise ValueError
        except ValueError:
            self.info.set("Enter 1-40 comma-separated integers.", color=RED)
            return
        self.name_a = self.algo.get()
        self.legend = [
            ("comparing", AMBER),
            ("swap / write", RED),
            ("pivot", PURPLE),
            ("sorted", GREEN),
        ]
        if self.race.get():
            self.name_b = self.algo_b.get()
            ra, rb = SORTS[self.name_a](values), SORTS[self.name_b](values)
            frames = race_frames(ra.frames, rb.frames)
            self.pseudo.show(
                (self.name_a, PSEUDO_SORT[self.name_a]),
                (self.name_b, PSEUDO_SORT[self.name_b]),
            )
            self.note = (
                f"{self.name_a}: {COMPLEXITY[self.name_a]}\n"
                f"{self.name_b}: {COMPLEXITY[self.name_b]}"
            )
        else:
            frames = SORTS[self.name_a](values).frames
            self.pseudo.show((self.name_a, PSEUDO_SORT[self.name_a]))
            self.note = COMPLEXITY[self.name_a]
        self.load(frames, autoplay)

    # ---- drawing ----
    def _bars(self, f, x0, x1, title, finished):
        b = self.board
        H = b.H
        vals, n = f["values"], len(f["values"])
        top, bottom = 84, H - 48
        gap = 6 if n <= 20 else 3
        bw = (x1 - x0 - 48 - gap * (n - 1)) / n
        lo, hi = min(vals), max(vals)
        span = max(hi - lo, 1)
        b.pill(
            (x0 + x1) / 2,
            44,
            title + ("  DONE" if finished else ""),
            GREEN if finished else TEXT,
            size=10,
        )
        b.txt(
            (x0 + x1) / 2,
            64,
            f"comparisons {f['comps']}   swaps/writes {f['swaps']}",
            MUTED,
            9,
            mono=True,
        )
        rng, done = f["rng"], f["done"]
        for i, v in enumerate(vals):
            ratio = (v - lo) / span
            bx1 = x0 + 24 + i * (bw + gap)
            bx2 = bx1 + bw
            by1 = bottom - (0.10 + 0.90 * ratio) * (bottom - top)
            col = gradient(BAR_GRADIENT, ratio)
            if i in done:
                col = mix(col, GREEN, 0.78)
            elif rng and not (rng[0] <= i <= rng[1]):
                col = mix(col, CANVAS, 0.62)
            if i in f["swap"]:
                col = RED
            elif i in f["cmp"]:
                col = AMBER
            elif i == f["pivot"]:
                col = PURPLE
            b.rrect(bx1, by1, bx2, bottom, min(6, bw / 2), fill=col, outline="")
            if bw >= 20:
                b.txt((bx1 + bx2) / 2, by1 - 10, str(v), TEXT, 9 if bw >= 26 else 8)
                b.txt((bx1 + bx2) / 2, bottom + 11, str(i), DIM, 8, mono=True)
            if i == f["pivot"]:
                cx = (bx1 + bx2) / 2
                b.create_polygon(
                    cx - 6,
                    by1 - 30,
                    cx + 6,
                    by1 - 30,
                    cx,
                    by1 - 21,
                    fill=PURPLE,
                    outline="",
                    tags="dyn",
                )
        if rng:
            xa = x0 + 24 + rng[0] * (bw + gap)
            xb = x0 + 24 + rng[1] * (bw + gap) + bw
            b.create_line(
                xa,
                bottom + 26,
                xb,
                bottom + 26,
                fill=INDIGO,
                width=3,
                capstyle="round",
                tags="dyn",
            )

    def render(self, f):
        b = self.board
        b.clear()
        W, H = b.W, b.H
        b.legend(self.legend, 20, H - 12)
        if "race" in f:
            fa, fb = f["race"]
            mid = W / 2
            i, na, nb = f["i"], f["na"], f["nb"]
            self._bars(fa, 0, mid - 8, "A: " + self.name_a, i >= na - 1)
            self._bars(fb, mid + 8, W, "B: " + self.name_b, i >= nb - 1)
            b.create_line(mid, 30, mid, H - 30, fill=BORDER, dash=(5, 5), tags="dyn")
            ops_a, ops_b = na - 1, nb - 1
            if i >= max(na, nb) - 1:
                if ops_a == ops_b:
                    res = f"Tie: both finished in {ops_a} steps"
                else:
                    win = "A" if ops_a < ops_b else "B"
                    nm = self.name_a if win == "A" else self.name_b
                    res = (
                        f"Winner: {win} ({nm}) with {min(ops_a, ops_b)} steps "
                        f"vs {max(ops_a, ops_b)}"
                    )
            elif i >= min(na, nb) - 1:
                first = "A" if na < nb else "B"
                res = f"{first} has finished first and is waiting for the other"
            else:
                res = "Both run one comparison / swap per step"
            stats = (
                f"A  comps {fa['comps']:>4}  swaps {fa['swaps']:>4}\n"
                f"B  comps {fb['comps']:>4}  swaps {fb['swaps']:>4}"
            )
            self.info.set(
                f"A: {fa['status']}\nB: {fb['status']}", res, stats, self.note
            )
            self.pseudo.highlight(fa["line"], fb["line"])
        else:
            self._bars(f, 0, W, self.name_a, f["line"] is None)
            self.info.set(
                f["status"],
                "",
                f"Comparisons: {f['comps']}\nSwaps / writes: {f['swaps']}",
                self.note,
            )
            self.pseudo.highlight(f["line"])
