"""Colour palette and colour maths. Pure Python (no tkinter), so the
algorithm layer can use it too."""

BG = "#080c18"
PANEL = "#0f1526"
PANEL_2 = "#182038"
BORDER = "#263152"
CANVAS = "#0b1122"
GRID = "#151d38"
CODE_BG = "#0c1220"

TEXT = "#e6ebf7"
MUTED = "#93a1c6"
DIM = "#5d6c94"

INDIGO = "#6366f1"
CYAN = "#22d3ee"
GREEN = "#34d399"
AMBER = "#fbbf24"
PINK = "#f472b6"
PURPLE = "#a78bfa"
RED = "#fb7185"
BLUE = "#60a5fa"
GOLD = "#facc15"

# node styles: (fill, outline, text colour, halo colour or None)
NODE = {
    "default": ("#16203a", "#4a5b8c", TEXT, None),
    "trail": ("#15294f", BLUE, "#dbeafe", None),
    "frontier": ("#251b48", PURPLE, "#ede9fe", None),
    "visited": ("#0d3b32", GREEN, "#d1fae5", None),
    "cmp": (PINK, "#fbcfe8", "#2a0a1c", PINK),
    "active": (AMBER, "#fde68a", "#1c1300", AMBER),
    "warn": (RED, "#fecdd3", "#2a0610", RED),
    "found": (GOLD, "#fef9c3", "#1c1500", GOLD),
    "path": ("#3b2f08", GOLD, "#fef3c7", GOLD),
}
GROUP_COLORS = [CYAN, PINK, AMBER, PURPLE, GREEN, BLUE, RED, "#fb923c"]


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, t):
    """Blend colour c1 towards c2 by t (0..1)."""
    a, b = _rgb(c1), _rgb(c2)
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(stops, t):
    t = max(0.0, min(1.0, t))
    seg = t * (len(stops) - 1)
    i = min(int(seg), len(stops) - 2)
    return mix(stops[i], stops[i + 1], seg - i)
