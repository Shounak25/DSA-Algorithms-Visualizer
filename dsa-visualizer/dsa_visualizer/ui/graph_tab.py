"""Graphs tab: BFS, DFS, Dijkstra, A*, components with draggable nodes."""

import random
import tkinter as tk

from ..algorithms.complexity import COMPLEXITY
from ..algorithms.graphs import (
    DEFAULT_EDGES,
    DEFAULT_POS,
    GRAPH_ALGOS,
    circle_layout,
    make_graph_frames,
    parse_edges,
)
from ..algorithms.pseudocode import PSEUDO_GRAPH
from ..colors import (
    CANVAS,
    GOLD,
    GREEN,
    GROUP_COLORS,
    MUTED,
    NODE,
    PANEL,
    PINK,
    RED,
    mix,
)
from .base_tab import BaseTab
from .widgets import label, set_entry


class GraphTab(BaseTab):
    NAME = "  Graphs  "

    def build_controls(self, p):
        self.pos = dict(DEFAULT_POS)
        self.edges = []
        self.weighted = True
        self.s = self.t = ""
        self.drag = None
        label(p, "Weighted Graph", 14, "bold").pack(anchor="w")
        label(
            p,
            "BFS, DFS, Dijkstra, A* and components. Drag vertices to "
            "rearrange them.",
            9,
            fg=MUTED,
            wraplength=250,
        ).pack(anchor="w", pady=(2, 6))
        self.section(p, "ALGORITHM")
        self.algo = self.combo(p, GRAPH_ALGOS, 2)
        self.section(p, "EDGES  (A-B:weight, ...)")
        self.edge_in = self.entry(p, DEFAULT_EDGES)
        self.section(p, "START VERTEX")
        self.start_in = self.entry(p, "A")
        self.section(p, "TARGET  (Dijkstra optional, A* required)")
        self.target_in = self.entry(p, "F")
        tk.Frame(p, bg=PANEL, height=8).pack()
        self.button(p, "Visualize", lambda: self.start(True), accent=True)
        self.button(p, "Random graph", self.random_graph)
        self.button(p, "Reset", self.reset)
        self.button(p, "Export GIF", self.export_gif)
        b = self.board
        b.bind("<ButtonPress-1>", self._grab)
        b.bind("<B1-Motion>", self._drag)
        b.bind("<ButtonRelease-1>", lambda e: setattr(self, "drag", None))

    # ---- geometry ----
    def px(self, n):
        x, y = self.pos[n]
        return 56 + x * (self.board.W - 112), 60 + y * (self.board.H - 120)

    def _grab(self, e):
        for n in self.pos:
            x, y = self.px(n)
            if (e.x - x) ** 2 + (e.y - y) ** 2 <= 32**2:
                self.drag = n
                return

    def _drag(self, e):
        if self.drag is None:
            return
        W, H = self.board.W, self.board.H
        self.pos[self.drag] = (
            min(1, max(0, (e.x - 56) / (W - 112))),
            min(1, max(0, (e.y - 60) / (H - 120))),
        )
        self.refresh()

    # ---- actions ----
    def random_graph(self):
        n = random.randint(6, 8)
        names = [chr(65 + i) for i in range(n)]
        pairs = {}
        for i in range(1, n):
            pairs[(names[random.randint(0, i - 1)], names[i])] = random.randint(1, 9)
        for _ in range(random.randint(2, 4)):
            a, c = random.sample(names, 2)
            key = tuple(sorted((a, c)))
            if key not in pairs and key[::-1] not in pairs:
                pairs[key] = random.randint(1, 9)
        set_entry(
            self.edge_in,
            ", ".join(f"{a}-{c}:{w}" for (a, c), w in sorted(pairs.items())),
        )
        set_entry(self.start_in, "A")
        set_entry(self.target_in, names[-1])
        self.pos = circle_layout(names)
        self.start(True)

    def reset(self):
        set_entry(self.edge_in, DEFAULT_EDGES)
        set_entry(self.start_in, "A")
        set_entry(self.target_in, "F")
        self.pos = dict(DEFAULT_POS)
        self.algo.current(2)
        self.start(False)

    def start(self, autoplay=True):
        self.pause()
        algo = self.algo.get()
        try:
            nodes, adj, edges, weighted = parse_edges(self.edge_in.get())
            s = self.start_in.get().strip().upper()
            t = self.target_in.get().strip().upper()
            if s not in adj:
                raise ValueError(f"Start vertex '{s}' is not in the graph.")
            if algo == "A*" and not t:
                raise ValueError("A* needs a target vertex.")
            if t and t not in adj:
                raise ValueError(f"Target vertex '{t}' is not in the graph.")
        except ValueError as exc:
            self.info.set(str(exc), color=RED)
            return
        if set(nodes) != set(self.pos):
            self.pos = (
                dict(DEFAULT_POS)
                if set(nodes) == set(DEFAULT_POS)
                else circle_layout(nodes)
            )
        self.edges, self.weighted, self.s = edges, weighted, s
        self.t = t if algo in ("Dijkstra", "A*") else ""
        frames = make_graph_frames(algo, adj, nodes, edges, self.pos, s, self.t)
        self.pseudo.show((algo, PSEUDO_GRAPH[algo]))
        self.note = COMPLEXITY[algo]
        self.legend = [("current", NODE["active"][1])]
        for key, text, style in (
            ("visited", "finished", "visited"),
            ("frontier", "queued / open", "frontier"),
            ("trail", "recursion stack", "trail"),
        ):
            if any(f.get(key) for f in frames):
                self.legend.append((text, NODE[style][1]))
        if any(f.get("path") for f in frames):
            self.legend.append(("shortest path", GOLD))
        if any(f.get("edge_hl") for f in frames):
            self.legend.append(("edge examined", PINK))
        self.load(frames, autoplay)

    def render(self, f):
        b = self.board
        b.clear()
        b.legend(self.legend, 20, 20)
        path = f.get("path") or []
        path_edges = {frozenset(pr) for pr in zip(path, path[1:])}
        tree = f.get("tree_edges", set())
        hl = frozenset(f["edge_hl"]) if f.get("edge_hl") else None
        for u, v, w in self.edges:
            (x1, y1), (x2, y2) = self.px(u), self.px(v)
            key = frozenset((u, v))
            if key in path_edges:
                b.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=mix(GOLD, CANVAS, 0.7),
                    width=12,
                    capstyle="round",
                    tags="dyn",
                )
                col, wd, dash, tc = GOLD, 5, None, GOLD
            elif key == hl:
                col, wd, dash, tc = PINK, 4, (7, 5), PINK
            elif key in tree:
                col, wd, dash, tc = GREEN, 4, None, GREEN
            else:
                col, wd, dash, tc = "#33416b", 3, None, MUTED
            b.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=col,
                width=wd,
                dash=dash,
                capstyle="round",
                tags="dyn",
            )
            if self.weighted:
                b.pill((x1 + x2) / 2, (y1 + y2) / 2, f"{w:g}", tc)
        visited, frontier = set(f.get("visited", ())), set(f.get("frontier", ()))
        trail, groups = set(f.get("trail", ())), f.get("groups", {})
        badge, active = f.get("badge", {}), f.get("active")
        for n in self.pos:
            x, y = self.px(n)
            if n in path:
                st = "path"
            elif n == active:
                st = "active"
            elif n in groups:
                st = "group"
            elif n in visited:
                st = "visited"
            elif n in frontier:
                st = "frontier"
            elif n in trail:
                st = "trail"
            else:
                st = "default"
            if st == "group":
                c = GROUP_COLORS[(groups[n] - 1) % len(GROUP_COLORS)]
                fill, outline, tcol, halo = mix(c, CANVAS, 0.55), c, "#ffffff", None
            else:
                fill, outline, tcol, halo = NODE[st]
            b.circle(x, y, 25, fill, outline, 2, halo)
            b.txt(x, y, n, tcol, 13, "bold")
            if n in badge:
                b.txt(x, y + 38, badge[n][0], badge[n][1], 9, "bold", mono=True)
            if n == self.s:
                b.pill(x, y - 40, "START", GREEN, size=7)
            elif n == self.t:
                b.pill(x, y - 40, "GOAL", PINK, size=7)
        self.info.set(f["status"], f.get("result", ""), f.get("stats", ""), self.note)
        self.pseudo.highlight(f.get("line"))
