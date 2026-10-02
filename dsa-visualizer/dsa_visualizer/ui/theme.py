"""Font selection. ``F`` / ``M`` build Tk font tuples for UI and monospace text."""

from tkinter import font as tkfont

FONT = "Segoe UI"
MONO = "Consolas"


def F(size, weight="normal"):
    return (FONT, size, weight)


def M(size, weight="normal"):
    return (MONO, size, weight)


def init_fonts(root):
    """Pick the best available UI / monospace fonts for this machine.

    Call once after the Tk root exists. ``F`` and ``M`` read the module-level
    ``FONT`` / ``MONO`` at call time, so widgets created afterwards use them.
    """
    global FONT, MONO
    fams = set(tkfont.families(root))
    FONT = next(
        (
            f
            for f in (
                "Segoe UI",
                "SF Pro Text",
                "Helvetica Neue",
                "Inter",
                "Ubuntu",
                "DejaVu Sans",
            )
            if f in fams
        ),
        "TkDefaultFont",
    )
    MONO = next(
        (
            f
            for f in (
                "Cascadia Code",
                "Consolas",
                "Menlo",
                "DejaVu Sans Mono",
                "Courier New",
            )
            if f in fams
        ),
        "TkFixedFont",
    )
