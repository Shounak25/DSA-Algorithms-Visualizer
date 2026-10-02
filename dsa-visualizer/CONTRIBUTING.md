# Contributing

## Setup
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -q
```

## Adding a new algorithm
1. **Engine** - add a `frames_<name>()` (trees/graphs) or `sort_<name>()` (sorting) function in
   `dsa_visualizer/algorithms/`. It must return a list of frames and must not import `tkinter`.
2. **Register it** in `TREE_ALGOS` / `GRAPH_ALGOS` / `SORTS` and its dispatcher.
3. **Teach the UI** about it: add pseudocode in `algorithms/pseudocode.py` (the `line` index in each
   frame highlights a line) and a complexity note in `algorithms/complexity.py`.
4. **Test it** in `tests/` - assert on the final frame and on any invariant (sortedness, balance...).
5. Run `black dsa_visualizer tests && pyflakes dsa_visualizer tests && pytest`.
