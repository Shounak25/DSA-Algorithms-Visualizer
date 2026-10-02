"""One-line complexity / usage notes for every algorithm."""

COMPLEXITY = {
    "In-order": "Time O(n) | Space O(h).  Left, node, right: on a BST this "
    "gives the keys in sorted order.",
    "Pre-order": "Time O(n) | Space O(h).  Node first, so it is handy for "
    "copying or serialising a tree.",
    "Post-order": "Time O(n) | Space O(h).  Children before the parent, used "
    "for deleting a tree or evaluating expressions.",
    "Level-order": "Time O(n) | Space O(w).  Breadth-first: uses a queue and "
    "visits the tree one level at a time.",
    "Search (BST)": "Time O(h) | Space O(1).  h is about log n for a balanced "
    "tree but n for a chain.",
    "Height": "Time O(n) | Space O(h).  Post-order recursion: a node needs both "
    "children's heights first.",
    "AVL insert": "Insert O(log n) | at most 2 rotations per insert.  Keeps "
    "|balance factor| <= 1 so the tree stays shallow.",
    "Min-heap build": "Insert O(log n) each | Space O(1) extra.  The smallest "
    "value always bubbles up to the root.",
    "Min-heap extract": "Extract O(log n) each, so n of them is O(n log n) "
    "(heap sort).",
    "Bubble sort": "Time O(n^2), O(n) if already sorted | Space O(1) | stable.",
    "Selection sort": "Time O(n^2) always | Space O(1) | not stable | at most "
    "n-1 swaps.",
    "Insertion sort": "Time O(n^2), O(n) if nearly sorted | Space O(1) | stable.",
    "Merge sort": "Time O(n log n) always | Space O(n) | stable.",
    "Quick sort": "Time O(n log n) average, O(n^2) worst | Space O(log n) | "
    "not stable.",
    "Heap sort": "Time O(n log n) always | Space O(1) | not stable.",
    "BFS": "Time O(V+E) | finds fewest-edge paths in an unweighted graph.",
    "DFS": "Time O(V+E) | goes deep first; good for cycles, components, "
    "topological order.",
    "Dijkstra": "Time O((V+E) log V) | shortest paths for non-negative weights.",
    "A*": "Dijkstra guided by a heuristic h.  Here h = straight-line distance "
    "on screen (scaled so it never overestimates), so drag nodes to "
    "change it.",
    "Components": "Time O(V+E) | flood-fill from every unvisited vertex; each "
    "colour is one component.",
}
