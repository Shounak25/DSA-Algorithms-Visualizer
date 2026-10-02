"""Trees tab: traversals, BST search, height, AVL insert, min-heap."""

import random
import tkinter as tk

from ..algorithms.complexity import COMPLEXITY
from ..algorithms.pseudocode import PSEUDO_TREE
from ..algorithms.trees import HEAP_ALGOS, TREE_ALGOS, make_tree_frames
from ..colors import CYAN, DIM, MUTED, NODE, PANEL, RED
from .base_tab import BaseTab
from .widgets import label, set_entry

TREE_LEGEND_KEYS = [
    ("visited", "visited", "visited"),
    ("frontier", "in queue", "frontier"),
    ("trail", "call stack / path", "trail"),
    ("cmp", "comparing", "cmp"),
    ("warn", "unbalanced", "warn"),
    ("found", "found / min", "found"),
]


class TreeTab(BaseTab):
    NAME = "  Trees  "

    def build_controls(self, p):
        label(p, "Trees & Heaps", 14, "bold").pack(anchor="w")
        label(
            p,
            "Traversals, BST search, AVL rotations and min-heaps, "
            "one step at a time.",
            9,
            fg=MUTED,
            wraplength=250,
        ).pack(anchor="w", pady=(2, 6))
        self.section(p, "ALGORITHM")
        self.algo = self.combo(p, TREE_ALGOS)
        self.section(p, "VALUES  (comma-separated integers)")
        self.values = self.entry(p, "8, 3, 10, 1, 6, 14, 4, 7, 13")
        self.section(p, "SEARCH TARGET  (Search only)")
        self.target = self.entry(p, "7")
        tk.Frame(p, bg=PANEL, height=8).pack()
        self.button(p, "Visualize", lambda: self.start(True), accent=True)
        self.button(p, "Random values", self.randomize)
        self.button(p, "Reset", self.reset)
        self.button(p, "Export GIF", self.export_gif)

    def randomize(self):
        vals = random.sample(range(1, 60), 9)
        set_entry(self.values, ", ".join(map(str, vals)))
        set_entry(self.target, str(random.choice(vals)))
        self.start(True)

    def reset(self):
        set_entry(self.values, "8, 3, 10, 1, 6, 14, 4, 7, 13")
        set_entry(self.target, "7")
        self.algo.current(0)
        self.start(False)

    def start(self, autoplay=True):
        self.pause()
        algo = self.algo.get()
        try:
            vals = [int(x) for x in self.values.get().split(",") if x.strip()]
            if not vals or len(vals) > 31:
                raise ValueError
            if algo not in HEAP_ALGOS and len(set(vals)) != len(vals):
                raise ValueError
        except ValueError:
            self.info.set("Enter 1-31 integers (unique, except for heaps).", color=RED)
            return
        target = None
        if algo == "Search (BST)":
            try:
                target = int(self.target.get())
            except ValueError:
                self.info.set("The search target must be an integer.", color=RED)
                return
        frames = make_tree_frames(algo, vals, target)
        self.pseudo.show((algo, PSEUDO_TREE[algo]))
        self.note = COMPLEXITY[algo]
        self.legend = [("current", NODE["active"][1])]
        for key, text, style in TREE_LEGEND_KEYS:
            if any(f.get(key) for f in frames):
                self.legend.append((text, NODE[style][1]))
        self.load(frames, autoplay)

    def render(self, f):
        b = self.board
        b.clear()
        W, H = b.W, b.H
        root, kids, labels = f["tree"]
        arr = f.get("array")
        reserve = 96 if arr is not None else 26
        sets = {
            k: set(f.get(k, ()))
            for k in ("visited", "frontier", "trail", "cmp", "warn")
        }
        active, found = f.get("active"), f.get("found")

        def style_of(n):
            if n == found:
                return "found"
            if n in sets["warn"]:
                return "warn"
            if n == active:
                return "active"
            if n in sets["cmp"]:
                return "cmp"
            if n in sets["visited"]:
                return "visited"
            if n in sets["frontier"]:
                return "frontier"
            if n in sets["trail"]:
                return "trail"
            return "default"

        b.legend(self.legend, 20, 20)
        if root is None:
            b.txt(W / 2, (H - reserve) / 2, "(empty)", DIM, 14)
        else:
            order, depth, counter = {}, {}, [0]

            def rec(n, d):
                l, r = kids[n]
                if l is not None:
                    rec(l, d + 1)
                order[n] = counter[0]
                depth[n] = d
                counter[0] += 1
                if r is not None:
                    rec(r, d + 1)

            rec(root, 0)
            count, levels = counter[0], max(depth.values())
            step = (W - 80) / count
            r = max(13, min(26, step * 0.42))
            top = 64
            avail = H - reserve - top - 24
            ystep = min(92, avail / max(levels, 1))
            top += max(0, min(60, (avail - ystep * levels) / 2))
            pos = {
                n: (40 + (order[n] + 0.5) * step, top + depth[n] * ystep) for n in order
            }
            for n in order:
                for c in kids[n]:
                    if c is None:
                        continue
                    hot = n in sets["trail"] and c in sets["trail"]
                    b.create_line(
                        *pos[n],
                        *pos[c],
                        fill=CYAN if hot else "#2c3a63",
                        width=4 if hot else 2.5,
                        capstyle="round",
                        tags="dyn",
                    )
            badge = f.get("badge", {})
            for n, (x, y) in pos.items():
                fill, outline, tcol, halo = NODE[style_of(n)]
                b.circle(x, y, r, fill, outline, 2, halo)
                b.txt(x, y, labels[n], tcol, 11 if r >= 20 else 9, "bold")
                if n in badge:
                    b.txt(x, y + r + 11, badge[n][0], badge[n][1], 8, "bold", mono=True)
        if arr is not None:
            n = len(arr)
            if n:
                bw = min(54, (W - 120) / n)
                x0 = (W - bw * n) / 2
                y0 = H - 78
                for i, v in enumerate(arr):
                    fill, outline, tcol, _ = NODE[style_of(i)]
                    b.rrect(
                        x0 + i * bw + 2,
                        y0,
                        x0 + (i + 1) * bw - 2,
                        y0 + 36,
                        6,
                        fill=fill,
                        outline=outline,
                        width=2,
                    )
                    b.txt(x0 + (i + 0.5) * bw, y0 + 18, str(v), tcol, 10, "bold")
                    b.txt(x0 + (i + 0.5) * bw, y0 + 48, str(i), DIM, 8, mono=True)
                b.txt(x0 - 8, y0 + 18, "array", DIM, 9, anchor="e")
            else:
                b.txt(W / 2, H - 60, "heap is empty", DIM, 10)
        self.info.set(f["status"], f.get("result", ""), f.get("stats", ""), self.note)
        self.pseudo.highlight(f.get("line"))
