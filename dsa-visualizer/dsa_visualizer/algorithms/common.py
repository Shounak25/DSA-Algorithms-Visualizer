"""Helpers shared by the algorithm modules."""


def join_items(items):
    """Format a list as ``a → b → c`` (or ``-`` when empty)."""
    return " → ".join(map(str, items)) if items else "-"
