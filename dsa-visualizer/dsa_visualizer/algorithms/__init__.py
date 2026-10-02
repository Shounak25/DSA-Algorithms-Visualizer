"""Pure-Python algorithm engines.

Nothing in this package imports tkinter. Every algorithm records its run as a
list of *frames* (plain dicts), which the UI layer replays. That separation
keeps the algorithms unit-testable without a display.
"""
