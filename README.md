# DSA Visualizer

An interactive, step-by-step playground for **20 classic data-structure and algorithm routines** -
trees, graphs and sorting - built with nothing but Python's standard library (Tkinter).

Every run is recorded as a list of frames, so you can **play, pause, step forward *and backward*,
scrub a timeline, change the speed, replay, and export a GIF**. A pseudocode panel highlights the
exact line being executed, and a status card shows live counters plus the complexity of the
algorithm.

| Trees & Heaps | Weighted Graphs | Sorting (with race mode) |
|---|---|---|
| ![AVL insert](docs/screenshots/trees-avl.png) | ![Dijkstra](docs/screenshots/graphs-dijkstra.png) | ![Quick sort](docs/screenshots/sorting-quick.png) |

## Features

| Area | Algorithms |
|---|---|
| **Trees** | In-order, Pre-order, Post-order, Level-order traversal - BST search - Tree height - **AVL insertion with rotations** (LL, RR, LR, RL) - Min-heap build and extract |
| **Graphs** | BFS, DFS, **Dijkstra**, **A\*** (straight-line heuristic), Connected components - custom weighted edges - **drag vertices with the mouse** |
| **Sorting** | Bubble, Selection, Insertion, Merge, Quick, Heap - **Race mode** runs two algorithms side by side on the same array |

Also: keyboard shortcuts, random input generators, input validation with friendly errors, GIF export,
and a dark theme that adapts its fonts to Windows, macOS and Linux.

### Keyboard shortcuts
`Space` play/pause - `Left` / `Right` step back/forward - `Home` / `End` first/last frame

## Quick start

Requires **Python 3.9+** with Tkinter (bundled with the python.org installers for Windows and macOS;
on Debian/Ubuntu run `sudo apt install python3-tk`).

```bash
git clone https://github.com/<your-username>/dsa-visualizer.git
cd dsa-visualizer

python main.py                # or:  python -m dsa_visualizer

# optional - enables the "Export GIF" button
pip install -r requirements.txt
```

## Project structure

```
dsa-visualizer/
├── main.py                     # launcher
├── dsa_visualizer/
│   ├── app.py                  # main window, ttk styles, shortcuts
│   ├── colors.py               # palette + colour maths (no tkinter)
│   ├── algorithms/             # pure Python engines - NO GUI imports
│   │   ├── trees.py            #   traversals, BST search, height, AVL, heaps
│   │   ├── graphs.py           #   BFS, DFS, Dijkstra, A*, components, edge parser
│   │   ├── sorting.py          #   6 sorts recorded via SortRec, race mode
│   │   ├── pseudocode.py       #   pseudocode shown next to each animation
│   │   ├── complexity.py       #   time/space notes per algorithm
│   │   └── common.py
│   └── ui/                     # Tkinter layer
│       ├── base_tab.py         #   playback engine, transport bar, GIF export
│       ├── tree_tab.py  graph_tab.py  sort_tab.py
│       ├── widgets.py          #   Board canvas, pseudocode panel, status card
│       └── theme.py            #   font selection
├── tests/                      # pytest suite for the algorithm layer
├── docs/ARCHITECTURE.md        # design notes
└── .github/workflows/ci.yml    # lint + tests on Python 3.9 / 3.11 / 3.12
```

## How it works

The key idea is a **record-then-replay architecture**:

1. An algorithm runs to completion *up front* and appends an immutable **frame** (a plain `dict`)
   at every meaningful step: the data snapshot, which pseudocode line is executing, a status
   message, and highlight sets (visited, frontier, comparing, ...).
2. A shared `BaseTab` owns the playback engine and only ever asks one question: *"render frame *i*"*.
3. Because frames are just data, **stepping backwards, scrubbing and replaying are free**, and
   algorithms can be unit-tested without a display.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for details.

## Testing

```bash
pip install -r requirements-dev.txt
pytest -q          # 79 tests, headless
```

The suite checks correctness invariants rather than just "does not crash": every sort produces
sorted output and leaves its input untouched, in-order traversal of a BST is sorted, AVL trees stay
balanced (height 4 for 15 sorted inserts instead of 15), Dijkstra and A\* agree on the shortest
path, and the edge parser rejects malformed input.

## Complexity reference

| Algorithm | Time | Space | Notes |
|---|---|---|---|
| Tree traversals / height | O(n) | O(h) | level-order uses O(w) |
| BST search | O(h) | O(1) | O(log n) balanced, O(n) for a chain |
| AVL insert | O(log n) | O(1) | at most 2 rotations |
| Heap insert / extract | O(log n) | O(1) | extract-all = heap sort |
| BFS / DFS / components | O(V+E) | O(V) | |
| Dijkstra | O((V+E) log V) | O(V) | non-negative weights |
| A\* | depends on heuristic | O(V) | admissible straight-line heuristic |
| Bubble / Selection / Insertion | O(n²) | O(1) | insertion & bubble are O(n) on sorted input |
| Merge sort | O(n log n) | O(n) | stable |
| Quick sort | O(n log n) avg, O(n²) worst | O(log n) | |
| Heap sort | O(n log n) | O(1) | |

## Roadmap ideas

- Red-black trees, tries, union-find
- Bellman-Ford, Kruskal / Prim, topological sort
- Save / load custom graphs as JSON
- Side-by-side race mode for graph algorithms


