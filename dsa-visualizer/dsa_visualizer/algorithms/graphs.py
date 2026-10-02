"""Graph algorithms. Each ``frames_*`` function returns a list of frame dicts."""

import heapq
import math

from ..colors import AMBER, DIM, GREEN
from .common import join_items

DEFAULT_EDGES = "A-B:4, A-D:2, B-C:3, B-E:7, D-E:1, C-F:5, E-F:2"
DEFAULT_POS = {
    "A": (0.10, 0.36),
    "B": (0.34, 0.12),
    "C": (0.68, 0.14),
    "D": (0.24, 0.80),
    "E": (0.53, 0.60),
    "F": (0.90, 0.52),
}
INF = float("inf")


def fmt(x):
    return "inf" if x == INF else f"{x:g}"


def circle_layout(nodes):
    pos = {}
    for i, n in enumerate(nodes):
        ang = 2 * math.pi * i / len(nodes) - math.pi / 2
        pos[n] = (0.5 + 0.40 * math.cos(ang), 0.5 + 0.38 * math.sin(ang))
    return pos


def parse_edges(text):
    edges, weighted = {}, False
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        w = 1.0
        if ":" in item:
            item, ws = item.rsplit(":", 1)
            try:
                w = float(ws)
            except ValueError:
                raise ValueError(f"'{ws.strip()}' is not a valid weight.")
            weighted = True
        parts = [p.strip().upper() for p in item.split("-")]
        if len(parts) != 2 or not all(parts) or parts[0] == parts[1]:
            raise ValueError(f"Bad edge '{item.strip()}'. Use A-B or A-B:4.")
        if w <= 0:
            raise ValueError("Edge weights must be positive.")
        key = tuple(sorted(parts))
        edges[key] = min(edges.get(key, w), w)
    if not edges:
        raise ValueError("Add at least one edge, e.g. A-B:4, B-C:2")
    nodes = sorted({n for e in edges for n in e})
    if len(nodes) > 20:
        raise ValueError("Use at most 20 vertices.")
    adj = {n: [] for n in nodes}
    for (u, v), w in edges.items():
        adj[u].append((v, w))
        adj[v].append((u, w))
    for n in adj:
        adj[n].sort()
    edge_list = [(u, v, w) for (u, v), w in sorted(edges.items())]
    return nodes, adj, edge_list, weighted


def _gemit(F_, line, msg, **kw):
    d = dict(line=line, status=msg)
    d.update(kw)
    F_.append(d)


def frames_bfs(adj, start):
    F_, visited, queue, seen, tree = [], [], [start], {start}, set()

    def emit(ln, msg, active=None, hl=None):
        _gemit(
            F_,
            ln,
            msg,
            active=active,
            visited=list(visited),
            frontier=list(queue),
            edge_hl=hl,
            tree_edges=set(tree),
            result="Visit order: " + join_items(visited),
            stats="Queue: [" + ", ".join(queue) + "]",
        )

    emit(0, f"Enqueue {start} and mark it discovered")
    while queue:
        u = queue.pop(0)
        emit(2, f"Dequeue {u}", u)
        visited.append(u)
        emit(3, f"Visit {u}", u)
        for v, _ in adj[u]:
            if v in seen:
                emit(5, f"{v} is already discovered: skip", u, (u, v))
            else:
                seen.add(v)
                queue.append(v)
                tree.add(frozenset((u, v)))
                emit(7, f"Discover {v} through {u} and enqueue it", u, (u, v))
    emit(None, "BFS complete")
    return F_


def frames_dfs(adj, start):
    F_, done, order, stack, tree = [], [], [], [], set()

    def emit(ln, msg, active=None, hl=None):
        _gemit(
            F_,
            ln,
            msg,
            active=active,
            visited=list(done),
            trail=list(stack),
            edge_hl=hl,
            tree_edges=set(tree),
            result="Visit order: " + join_items(order),
            stats="Stack: " + (" > ".join(stack) or "-"),
        )

    def go(u):
        stack.append(u)
        order.append(u)
        emit(1, f"Enter {u} and mark it visited", u)
        for v, _ in adj[u]:
            if v in order:
                emit(3, f"{v} is already visited: skip", u, (u, v))
            else:
                tree.add(frozenset((u, v)))
                emit(4, f"Go deeper: {u} -> {v}", u, (u, v))
                go(v)
        stack.pop()
        done.append(u)
        emit(5, f"{u} is fully explored: backtrack", stack[-1] if stack else None)

    go(start)
    emit(None, "DFS complete")
    return F_


def _path_to(parent, target):
    path, n = [], target
    while n is not None:
        path.append(n)
        n = parent.get(n)
    return path[::-1]


def frames_dijkstra(adj, nodes, start, target):
    dist = {n: INF for n in nodes}
    dist[start] = 0
    parent, final, pq, F_ = {}, [], [(0, start)], []

    def pq_view():
        return sorted({(d, n) for d, n in pq if n not in final and d == dist[n]})

    def emit(ln, msg, active=None, hl=None, **kw):
        badge = {
            n: (
                fmt(dist[n]),
                GREEN if n in final else (AMBER if dist[n] < INF else DIM),
            )
            for n in nodes
        }
        d = dict(
            active=active,
            visited=list(final),
            frontier=[n for _, n in pq_view()],
            edge_hl=hl,
            tree_edges={frozenset((v, p)) for v, p in parent.items()},
            badge=badge,
            result="Finalized: " + join_items(final),
            stats="PQ: "
            + (", ".join(f"{n}({fmt(d_)})" for d_, n in pq_view()) or "empty"),
        )
        d.update(kw)
        _gemit(F_, ln, msg, **d)

    emit(0, f"dist[{start}] = 0, every other distance = inf", start)
    emit(1, f"Push ({start}, 0) into the priority queue")
    while pq:
        d, u = heapq.heappop(pq)
        if u in final:
            emit(4, f"Skip the stale entry ({u}, {fmt(d)})")
            continue
        emit(3, f"Pop the closest unfinished vertex: {u} (distance {fmt(d)})", u)
        final.append(u)
        emit(5, f"Finalize {u}: its shortest distance {fmt(d)} is now exact", u)
        if u == target:
            break
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                old = fmt(dist[v])
                dist[v] = nd
                parent[v] = u
                heapq.heappush(pq, (nd, v))
                emit(
                    8,
                    f"Relax {u}-{v}: {fmt(d)} + {fmt(w)} = {fmt(nd)} < {old}, "
                    f"so update dist[{v}]",
                    u,
                    (u, v),
                )
            else:
                emit(
                    7,
                    f"{u}-{v}: {fmt(d)} + {fmt(w)} = {fmt(nd)} >= "
                    f"{fmt(dist[v])}, no improvement",
                    u,
                    (u, v),
                )
    if target:
        if target in final:
            path = _path_to(parent, target)
            emit(
                9,
                f"Shortest path {start} to {target}: {join_items(path)} "
                f"(cost {fmt(dist[target])})",
                None,
                path=path,
                result=f"Path: {join_items(path)}   cost = {fmt(dist[target])}",
            )
        else:
            emit(
                9,
                f"{target} is unreachable from {start}",
                None,
                result=f"No path to {target}",
            )
    else:
        emit(None, "All reachable distances found")
    return F_


def frames_astar(adj, nodes, edges, pos, start, target):
    def d(a, b):
        return math.hypot(pos[a][0] - pos[b][0], pos[a][1] - pos[b][1])

    ratios = [w / d(u, v) for u, v, w in edges if d(u, v) > 1e-9]
    scale = min(ratios) if ratios else 0.0

    def h(n):
        return scale * d(n, target)

    g = {start: 0}
    parent, closed, openq, F_ = {}, [], [(h(start), start)], []

    def open_nodes():
        return sorted({n for _, n in openq if n not in closed})

    def emit(ln, msg, active=None, hl=None, **kw):
        badge = {
            n: (
                f"{g[n]:g}+{h(n):.1f}={g[n] + h(n):.1f}",
                GREEN if n in closed else AMBER,
            )
            for n in g
        }
        dd = dict(
            active=active,
            visited=list(closed),
            frontier=open_nodes(),
            edge_hl=hl,
            badge=badge,
            tree_edges={frozenset((v, p)) for v, p in parent.items()},
            result="Closed: " + join_items(closed),
            stats="Open: "
            + (", ".join(open_nodes()) or "empty")
            + "\nBadge = g + h = f",
        )
        dd.update(kw)
        _gemit(F_, ln, msg, **dd)

    emit(0, f"g[{start}] = 0, h = {h(start):.1f}. Put {start} in the open set", start)
    while openq:
        f, u = heapq.heappop(openq)
        if u in closed:
            continue
        emit(
            2,
            f"Pick the open vertex with the smallest f = g + h: {u} " f"(f = {f:.1f})",
            u,
        )
        if u == target:
            path = _path_to(parent, target)
            emit(
                3,
                f"Reached the goal {target}: cost {g[target]:g}",
                None,
                path=path,
                result=f"Path: {join_items(path)}   cost = {g[target]:g}",
            )
            return F_
        closed.append(u)
        emit(4, f"Move {u} to the closed set", u)
        for v, w in adj[u]:
            t = g[u] + w
            if t < g.get(v, INF):
                g[v] = t
                parent[v] = u
                heapq.heappush(openq, (t + h(v), v))
                emit(
                    8,
                    f"g[{v}] = {g[u]:g} + {w:g} = {t:g};  f = {t:g} + "
                    f"{h(v):.1f} = {t + h(v):.1f}",
                    u,
                    (u, v),
                )
            else:
                emit(7, f"No better route to {v} through {u}", u, (u, v))
    emit(
        9,
        f"Open set is empty: {target} is unreachable",
        None,
        result=f"No path to {target}",
    )
    return F_


def frames_components(adj, nodes):
    F_, groups, comp = [], {}, [0]

    def emit(ln, msg, active=None, hl=None):
        by = {}
        for n, c in groups.items():
            by.setdefault(c, []).append(n)
        res = "  ".join("{" + ", ".join(sorted(v)) + "}" for _, v in sorted(by.items()))
        _gemit(
            F_,
            ln,
            msg,
            active=active,
            groups=dict(groups),
            edge_hl=hl,
            result=res or "-",
            stats=f"Components found: {comp[0]}",
        )

    emit(0, "count = 0")
    for s in nodes:
        if s in groups:
            emit(1, f"{s} already belongs to a component: skip", s)
            continue
        comp[0] += 1
        groups[s] = comp[0]
        emit(3, f"{s} is unvisited: start component #{comp[0]}", s)
        queue = [s]
        while queue:
            u = queue.pop(0)
            for v, _ in adj[u]:
                if v not in groups:
                    groups[v] = comp[0]
                    queue.append(v)
                    emit(3, f"{v} joins component #{comp[0]} (via {u})", u, (u, v))
    emit(4, f"The graph has {comp[0]} connected component(s)")
    return F_


GRAPH_ALGOS = ["BFS", "DFS", "Dijkstra", "A*", "Components"]


def make_graph_frames(algo, adj, nodes, edges, pos, start, target):
    if algo == "BFS":
        return frames_bfs(adj, start)
    if algo == "DFS":
        return frames_dfs(adj, start)
    if algo == "Dijkstra":
        return frames_dijkstra(adj, nodes, start, target)
    if algo == "A*":
        return frames_astar(adj, nodes, edges, pos, start, target)
    return frames_components(adj, nodes)
