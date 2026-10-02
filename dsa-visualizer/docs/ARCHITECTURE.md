# Architecture

## Layers

```
   ┌──────────────────────────── ui/ (Tkinter) ────────────────────────────┐
   │ app.py ──► TreeTab / GraphTab / SortTab ──► BaseTab (playback engine) │
   │                          │                       │                    │
   │                    render(frame)          widgets.py, theme.py        │
   └──────────────────────────┼────────────────────────────────────────────┘
                              │  list[dict]  (frames)
   ┌──────────────────────────┴───────── algorithms/ (pure Python) ────────┐
   │ trees.py   graphs.py   sorting.py   pseudocode.py   complexity.py      │
   └───────────────────────────────────────────────────────────────────────┘
```

**Rule:** `algorithms/` never imports `tkinter`. Dependencies point downward only, which keeps the
engines unit-testable in CI (no display) and reusable in a different front end (web, CLI, notebook).

## The frame contract

Each algorithm returns `list[dict]`. Keys the UI understands:

| Key | Used by | Meaning |
|---|---|---|
| `line` | all | index of the pseudocode line to highlight (`None` = no line) |
| `status` | all | one-sentence description of this step |
| `result`, `stats` | all | text shown on the status card |
| `tree` | trees | snapshot `(root, {node: (left, right)}, {node: label})` |
| `visited`, `frontier`, `trail`, `active` | trees, graphs | node sets that decide node colours |
| `badge` | trees, graphs | `{node: (text, colour)}` small label under a node (distance, `bf`, ...) |
| `edge_hl`, `path` | graphs | edges to highlight / final shortest path |
| `values`, `cmp`, `swap`, `pivot`, `done`, `rng` | sorting | array snapshot and bar highlights |
| `race` | sorting | pair of sort frames for race mode |

Frames are snapshots (copies), never references to live state, so any frame can be rendered
independently of the others. That is what makes step-back and scrubbing trivial.

## Playback engine (`ui/base_tab.py`)

`BaseTab` owns `frames`, `idx`, and the Tk `after()` timer. Subclasses implement three hooks:

- `build_controls(parent)` - the left-hand control panel,
- `start(autoplay)` - parse inputs, run the algorithm, call `load(frames)`,
- `render(frame)` - draw one frame on the canvas.

Play, pause, step, scrub, replay, speed, resize-safe redraw and GIF export live once, in the base
class, and all three tabs inherit them.

## Recording sorts (`SortRec`)

Sorting algorithms are written as ordinary loops that call `rec.compare(i, j, line)`,
`rec.swap(i, j, line)` or `rec.write(k, v, line)`. The recorder mutates its array, updates the
comparison/swap counters and appends a frame, so the algorithms stay readable and instrumented
uniformly. Race mode simply zips two recordings, padding the shorter one with its last frame.

## Design decisions

- **Standard library only.** Tkinter keeps installation to zero steps; Pillow is optional (GIF export).
- **Font fallbacks.** `theme.init_fonts()` picks the first available family per OS, so the UI looks
  right on Windows, macOS and Linux without bundling fonts.
- **Debounced resize.** `Board` redraws 40 ms after the last `<Configure>` event to avoid thrashing.
- **Validated input.** User input is parsed into friendly `ValueError`s, shown in red on the status card rather
  than crashing.
