"""Tree algorithms. Each ``frames_*`` function returns a list of frame dicts."""

import heapq

from ..colors import GREEN, RED
from .common import join_items


class TreeState:
    """Mutable binary tree. Node ids are hashable keys; labels are strings."""

    def __init__(self):
        self.root = None
        self.kids = {}
        self.labels = {}

    def add(self, key, text=None):
        self.kids[key] = [None, None]
        self.labels[key] = str(key if text is None else text)

    def snap(self):
        return (
            self.root,
            {k: tuple(v) for k, v in self.kids.items()},
            dict(self.labels),
        )


def tframe(tree, line, status, **kw):
    f = {"tree": tree.snap(), "line": line, "status": status}
    f.update(kw)
    return f


def build_bst(values):
    t = TreeState()
    for v in values:
        t.add(v)
        if t.root is None:
            t.root = v
            continue
        cur = t.root
        while True:
            side = 0 if v < cur else 1
            nxt = t.kids[cur][side]
            if nxt is None:
                t.kids[cur][side] = v
                break
            cur = nxt
    return t


def bst_height(t):
    def rec(n):
        if n is None:
            return 0
        return 1 + max(rec(t.kids[n][0]), rec(t.kids[n][1]))

    return rec(t.root)


def frames_depth_first(algo, values):
    t = build_bst(values)
    total = len(values)
    fn = algo.lower().replace("-", "")
    seq = {"In-order": "LVR", "Pre-order": "VLR", "Post-order": "LRV"}[algo]
    line = {
        "In-order": {"L": 2, "V": 3, "R": 4},
        "Pre-order": {"V": 2, "L": 3, "R": 4},
        "Post-order": {"L": 2, "R": 3, "V": 4},
    }[algo]
    F_, visited, stack = [], [], []

    def emit(ln, msg, active):
        F_.append(
            tframe(
                t,
                ln,
                msg,
                active=active,
                visited=list(visited),
                trail=list(stack),
                result="Visited: " + join_items(visited),
                stats=f"Visited {len(visited)} of {total} nodes",
            )
        )

    def walk(n):
        stack.append(n)
        emit(0, f"Call {fn}({n}).   Call stack: {join_items(stack)}", n)
        for step in seq:
            if step == "V":
                visited.append(n)
                emit(line["V"], f"Visit node {n}", n)
            else:
                side = 0 if step == "L" else 1
                child = t.kids[n][side]
                nm = "left" if side == 0 else "right"
                if child is None:
                    emit(1, f"The {nm} child of {n} is null, so return", n)
                else:
                    emit(line[step], f"Recurse into the {nm} child ({child})", n)
                    walk(child)
        stack.pop()

    walk(t.root)
    emit(None, "Traversal complete", None)
    return F_


def frames_level_order(values):
    t = build_bst(values)
    F_, visited, queue = [], [], [t.root]

    def emit(ln, msg, active=None):
        F_.append(
            tframe(
                t,
                ln,
                msg,
                active=active,
                visited=list(visited),
                frontier=list(queue),
                result="Visited: " + join_items(visited),
                stats="Queue: [" + ", ".join(map(str, queue)) + "]",
            )
        )

    emit(0, f"Put the root ({t.root}) into the queue")
    while queue:
        n = queue.pop(0)
        emit(2, f"Dequeue {n}", n)
        visited.append(n)
        emit(3, f"Visit node {n}", n)
        kids = [c for c in t.kids[n] if c is not None]
        queue.extend(kids)
        emit(
            4,
            f"Enqueue the children of {n}: "
            + (", ".join(map(str, kids)) or "none (leaf)"),
            n,
        )
    emit(None, "Traversal complete")
    return F_


def frames_search(values, target):
    t = build_bst(values)
    F_, passed, steps = [], [], [0]

    def emit(ln, msg, active=None, **kw):
        d = dict(
            visited=list(passed),
            trail=passed + ([active] if active is not None else []),
            stats=f"Comparisons: {steps[0]}",
            result=f"Searching for {target}",
        )
        d.update(kw)
        F_.append(tframe(t, ln, msg, active=active, **d))

    node = t.root
    emit(0, f"Start at the root ({node}); searching for {target}", node)
    while node is not None:
        steps[0] += 1
        if node == target:
            emit(
                2,
                f"{target} == {node}: found after {steps[0]} comparison(s)!",
                None,
                found=node,
                trail=passed + [node],
                result=f"Found {target}",
            )
            return F_
        go_left = target < node
        emit(
            2,
            f"Compare {target} with {node}:  {target} "
            f"{'<' if go_left else '>'} {node}",
            node,
        )
        emit(3, f"Go {'left' if go_left else 'right'}", node)
        passed.append(node)
        node = t.kids[passed[-1]][0 if go_left else 1]
    emit(
        4,
        f"Reached a null link, so {target} is not in the tree",
        None,
        result=f"{target} not found",
    )
    return F_


def frames_height(values):
    t = build_bst(values)
    F_, heights, stack = [], {}, []

    def emit(ln, msg, active=None, **kw):
        d = dict(
            trail=list(stack),
            visited=list(heights),
            badge={k: (f"h={v}", GREEN) for k, v in heights.items()},
            result="Heights are computed bottom-up",
            stats=f"Nodes finished: {len(heights)} of {len(values)}",
        )
        d.update(kw)
        F_.append(tframe(t, ln, msg, active=active, **d))

    def rec(n):
        stack.append(n)
        emit(0, f"height({n})", n)
        l, r = t.kids[n]
        hl = hr = 0
        if l is None:
            emit(1, f"Left child of {n} is null: height 0", n)
        else:
            emit(2, f"Ask the left subtree of {n} for its height", n)
            hl = rec(l)
        if r is None:
            emit(1, f"Right child of {n} is null: height 0", n)
        else:
            emit(3, f"Ask the right subtree of {n} for its height", n)
            hr = rec(r)
        h = 1 + max(hl, hr)
        heights[n] = h
        emit(4, f"height({n}) = 1 + max({hl}, {hr}) = {h}", n)
        stack.pop()
        return h

    total = rec(t.root)
    emit(
        None,
        f"Tree height = {total} (nodes on the longest root-to-leaf path)",
        result=f"Height = {total}",
    )
    return F_


def frames_avl(values):
    t = TreeState()
    H, F_, rotations, inserted = {}, [], [0], []

    def h(n):
        return H[n] if n is not None else 0

    def bf(n):
        l, r = t.kids[n]
        return h(l) - h(r)

    def upd(n):
        l, r = t.kids[n]
        H[n] = 1 + max(h(l), h(r))

    def badges():
        return {
            n: (f"bf {bf(n):+d}", RED if abs(bf(n)) > 1 else "#7dd3c8") for n in t.kids
        }

    def emit(ln, msg, active=None, **kw):
        d = dict(
            badge=badges(),
            result="Inserted: " + ", ".join(map(str, inserted)),
            stats=f"Rotations so far: {rotations[0]}    Height: {h(t.root)}",
        )
        d.update(kw)
        F_.append(tframe(t, ln, msg, active=active, **d))

    def rot_right(y):
        x = t.kids[y][0]
        t.kids[y][0] = t.kids[x][1]
        t.kids[x][1] = y
        upd(y)
        upd(x)
        rotations[0] += 1
        return x

    def rot_left(x):
        y = t.kids[x][1]
        t.kids[x][1] = t.kids[y][0]
        t.kids[y][0] = x
        upd(x)
        upd(y)
        rotations[0] += 1
        return y

    def relink(parent, old, new):
        if parent is None:
            t.root = new
        else:
            t.kids[parent][0 if t.kids[parent][0] == old else 1] = new

    for v in values:
        inserted.append(v)
        t.add(v)
        H[v] = 1
        if t.root is None:
            t.root = v
            emit(2, f"The tree is empty, so {v} becomes the root", v)
            continue
        path, cur = [], t.root
        emit(0, f"Insert {v}: start at the root", cur)
        while True:
            path.append(cur)
            side = 0 if v < cur else 1
            emit(
                1,
                f"{v} {'<' if side == 0 else '>'} {cur}, go "
                f"{'left' if side == 0 else 'right'}",
                cur,
                trail=list(path),
            )
            nxt = t.kids[cur][side]
            if nxt is None:
                break
            cur = nxt
        t.kids[cur][side] = v
        emit(
            2,
            f"Attach {v} as the {'left' if side == 0 else 'right'} " f"child of {cur}",
            v,
            trail=path + [v],
        )
        for i in range(len(path) - 1, -1, -1):
            n = path[i]
            upd(n)
            b = bf(n)
            emit(
                4,
                f"Update the height of {n}; balance factor = {b:+d}",
                n,
                trail=path[: i + 1],
            )
            if abs(b) <= 1:
                continue
            parent = path[i - 1] if i > 0 else None
            emit(
                5,
                f"Node {n} is unbalanced (balance factor {b:+d}): rebalance",
                None,
                warn=[n],
                trail=path[: i + 1],
            )
            l, r = t.kids[n]
            if b > 1:
                if bf(l) >= 0:
                    new = rot_right(n)
                    relink(parent, n, new)
                    emit(6, f"Left-Left case: rotate right at {n}", new)
                else:
                    t.kids[n][0] = rot_left(l)
                    upd(n)
                    emit(8, f"Left-Right case: first rotate left at {l}", n, warn=[n])
                    new = rot_right(n)
                    relink(parent, n, new)
                    emit(8, f"...then rotate right at {n}", new)
            else:
                if bf(r) <= 0:
                    new = rot_left(n)
                    relink(parent, n, new)
                    emit(7, f"Right-Right case: rotate left at {n}", new)
                else:
                    t.kids[n][1] = rot_right(r)
                    upd(n)
                    emit(9, f"Right-Left case: first rotate right at {r}", n, warn=[n])
                    new = rot_left(n)
                    relink(parent, n, new)
                    emit(9, f"...then rotate left at {n}", new)
            break
    plain = bst_height(build_bst(values))
    emit(
        None,
        f"All {len(values)} keys inserted and the tree stayed balanced",
        result=f"AVL height {h(t.root)} vs {plain} for a plain BST "
        f"built in the same order",
    )
    return F_


def heap_tree(a):
    t = TreeState()
    n = len(a)
    for i in range(n):
        t.kids[i] = [
            2 * i + 1 if 2 * i + 1 < n else None,
            2 * i + 2 if 2 * i + 2 < n else None,
        ]
        t.labels[i] = str(a[i])
    t.root = 0 if n else None
    return t


def frames_heap_build(values):
    a, F_, swaps = [], [], [0]

    def emit(ln, msg, **kw):
        d = dict(
            array=list(a),
            stats=f"Swaps: {swaps[0]}    Size: {len(a)}",
            result="Array: [" + ", ".join(map(str, a)) + "]",
        )
        d.update(kw)
        F_.append(tframe(heap_tree(a), ln, msg, **d))

    emit(0, "Start with an empty min-heap and insert the values one by one")
    for v in values:
        a.append(v)
        i = len(a) - 1
        emit(1, f"Insert {v}: append it at index {i}", active=i)
        while i > 0:
            p = (i - 1) // 2
            if a[i] < a[p]:
                emit(3, f"{a[i]} < parent {a[p]}, so swap them", cmp=[p], active=i)
                a[i], a[p] = a[p], a[i]
                swaps[0] += 1
                i = p
                emit(4, f"Swapped: {a[i]} moved up to index {i}", active=i)
            else:
                emit(
                    3,
                    f"{a[i]} >= parent {a[p]}: heap property holds, stop",
                    cmp=[p],
                    active=i,
                )
                break
    emit(None, "Min-heap built: the smallest value sits at the root", found=0)
    return F_


def frames_heap_extract(values):
    a = list(values)
    heapq.heapify(a)
    out, swaps, F_ = [], [0], []

    def emit(ln, msg, **kw):
        d = dict(
            array=list(a),
            stats=f"Swaps: {swaps[0]}    Size: {len(a)}",
            result="Output: " + (", ".join(map(str, out)) or "-"),
        )
        d.update(kw)
        F_.append(tframe(heap_tree(a), ln, msg, **d))

    emit(0, "Start from a valid min-heap (built with heapify)")
    while a:
        emit(1, f"The minimum is the root: {a[0]}", found=0)
        mn = a[0]
        last = a.pop()
        if a:
            a[0] = last
            emit(
                2,
                f"Remove {mn} and move the last element ({last}) to the root",
                active=0,
            )
            i = 0
            while True:
                kids = [c for c in (2 * i + 1, 2 * i + 2) if c < len(a)]
                if not kids:
                    emit(4, f"{a[i]} has no children: done", active=i)
                    break
                s = i
                for c in kids:
                    if a[c] < a[s]:
                        s = c
                emit(
                    4,
                    f"Compare {a[i]} with its children " f"{[a[c] for c in kids]}",
                    active=i,
                    cmp=kids,
                )
                if s == i:
                    emit(4, f"{a[i]} <= its children: heap property restored", active=i)
                    break
                a[i], a[s] = a[s], a[i]
                swaps[0] += 1
                i = s
                emit(
                    5,
                    f"Swapped with the smaller child; {a[i]} now at " f"index {i}",
                    active=i,
                )
        out.append(mn)
        emit(6, f"Output {mn}")
    emit(None, "Heap is empty: values came out in sorted order")
    return F_


TREE_ALGOS = [
    "In-order",
    "Pre-order",
    "Post-order",
    "Level-order",
    "Search (BST)",
    "Height",
    "AVL insert",
    "Min-heap build",
    "Min-heap extract",
]
HEAP_ALGOS = {"Min-heap build", "Min-heap extract"}


def make_tree_frames(algo, values, target=None):
    if algo in ("In-order", "Pre-order", "Post-order"):
        return frames_depth_first(algo, values)
    if algo == "Level-order":
        return frames_level_order(values)
    if algo == "Search (BST)":
        return frames_search(values, target)
    if algo == "Height":
        return frames_height(values)
    if algo == "AVL insert":
        return frames_avl(values)
    if algo == "Min-heap build":
        return frames_heap_build(values)
    return frames_heap_extract(values)
