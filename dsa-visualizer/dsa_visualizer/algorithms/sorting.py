"""Sorting algorithms, recorded step by step through :class:`SortRec`."""


class SortRec:
    def __init__(self, values):
        self.a = list(values)
        self.n = len(values)
        self.frames = []
        self.comps = 0
        self.swaps = 0
        self.done = set()

    def emit(self, line, msg, cmp=(), swap=(), pivot=None, rng=None):
        self.frames.append(
            dict(
                values=self.a[:],
                cmp=tuple(cmp),
                swap=tuple(swap),
                pivot=pivot,
                done=frozenset(self.done),
                rng=rng,
                line=line,
                status=msg,
                comps=self.comps,
                swaps=self.swaps,
            )
        )

    def compare(self, i, j, line, **kw):
        self.comps += 1
        kw.setdefault("cmp", (i, j))
        self.emit(line, f"Compare a[{i}] = {self.a[i]} with a[{j}] = {self.a[j]}", **kw)

    def swap(self, i, j, line, **kw):
        self.a[i], self.a[j] = self.a[j], self.a[i]
        self.swaps += 1
        self.emit(line, f"Swap positions {i} and {j}", swap=(i, j), **kw)

    def write(self, k, val, line, **kw):
        self.a[k] = val
        self.swaps += 1
        self.emit(line, f"Write {val} into position {k}", swap=(k,), **kw)

    def finish(self):
        self.done = set(range(self.n))
        self.emit(None, "Sorted")
        return self


def sort_bubble(values):
    r = SortRec(values)
    for end in range(r.n - 1, 0, -1):
        swapped = False
        r.emit(
            0,
            f"Pass: bubble the largest of a[0..{end}] to position {end}",
            rng=(0, end),
        )
        for i in range(end):
            r.compare(i, i + 1, 3, rng=(0, end))
            if r.a[i] > r.a[i + 1]:
                r.swap(i, i + 1, 4, rng=(0, end))
                swapped = True
        r.done.add(end)
        if not swapped:
            r.emit(6, "No swaps in this pass: already sorted, stop early")
            break
    return r.finish()


def sort_selection(values):
    r = SortRec(values)
    for i in range(r.n - 1):
        m = i
        r.emit(
            1,
            f"Assume a[{i}] = {r.a[i]} is the smallest of the unsorted part",
            cmp=(i,),
            rng=(i, r.n - 1),
        )
        for j in range(i + 1, r.n):
            r.compare(m, j, 3, rng=(i, r.n - 1))
            if r.a[j] < r.a[m]:
                m = j
        if m != i:
            r.swap(i, m, 4, rng=(i, r.n - 1))
        else:
            r.emit(
                4, f"a[{i}] is already the smallest: no swap needed", rng=(i, r.n - 1)
            )
        r.done.add(i)
    return r.finish()


def sort_insertion(values):
    r = SortRec(values)
    r.done = {0}
    for i in range(1, r.n):
        r.emit(
            1,
            f"Take the key a[{i}] = {r.a[i]} and insert it into the " f"sorted prefix",
            cmp=(i,),
        )
        j = i
        while j > 0:
            r.compare(j - 1, j, 2)
            if r.a[j - 1] > r.a[j]:
                r.swap(j - 1, j, 3)
                j -= 1
            else:
                break
        r.done = set(range(i + 1))
    return r.finish()


def sort_merge(values):
    r = SortRec(values)

    def ms(lo, hi):
        if lo >= hi:
            return
        mid = (lo + hi) // 2
        r.emit(2, f"Split a[{lo}..{hi}] at {mid}", rng=(lo, hi))
        ms(lo, mid)
        ms(mid + 1, hi)
        left, right = r.a[lo : mid + 1], r.a[mid + 1 : hi + 1]
        i = j = 0
        k = lo
        rng = (lo, hi)
        r.emit(
            4, f"Merge the sorted halves a[{lo}..{mid}] and a[{mid + 1}..{hi}]", rng=rng
        )
        while i < len(left) and j < len(right):
            r.comps += 1
            r.emit(
                5,
                f"Compare {left[i]} (left) with {right[j]} (right)",
                cmp=(lo + i, mid + 1 + j),
                rng=rng,
            )
            if left[i] <= right[j]:
                r.write(k, left[i], 6, rng=rng)
                i += 1
            else:
                r.write(k, right[j], 6, rng=rng)
                j += 1
            k += 1
        while i < len(left):
            r.write(k, left[i], 7, rng=rng)
            i += 1
            k += 1
        while j < len(right):
            r.write(k, right[j], 7, rng=rng)
            j += 1
            k += 1

    ms(0, r.n - 1)
    return r.finish()


def sort_quick(values):
    r = SortRec(values)

    def qs(lo, hi):
        if lo > hi:
            return
        if lo == hi:
            r.done.add(lo)
            r.emit(1, f"Single element a[{lo}]: already in place", rng=(lo, hi))
            return
        rng = (lo, hi)
        pivot, i = r.a[hi], lo
        r.emit(
            2, f"Pivot = a[{hi}] = {pivot}. Partition a[{lo}..{hi}]", pivot=hi, rng=rng
        )
        for j in range(lo, hi):
            r.compare(j, hi, 4, cmp=(j,), pivot=hi, rng=rng)
            if r.a[j] < pivot:
                if i != j:
                    r.swap(i, j, 5, pivot=hi, rng=rng)
                i += 1
        if i != hi:
            r.swap(i, hi, 6, rng=rng)
        r.done.add(i)
        r.emit(6, f"Pivot {pivot} is now in its final position {i}", pivot=i, rng=rng)
        qs(lo, i - 1)
        qs(i + 1, hi)

    qs(0, r.n - 1)
    return r.finish()


def sort_heap(values):
    r = SortRec(values)

    def sift(i, size):
        rng = (0, size - 1)
        while True:
            l, rt, m = 2 * i + 1, 2 * i + 2, i
            if l < size:
                r.comps += 1
                r.emit(
                    6,
                    f"Compare child a[{l}] = {r.a[l]} with a[{m}] = {r.a[m]}",
                    cmp=(l, m),
                    rng=rng,
                )
                if r.a[l] > r.a[m]:
                    m = l
            if rt < size:
                r.comps += 1
                r.emit(
                    7,
                    f"Compare child a[{rt}] = {r.a[rt]} with a[{m}] = {r.a[m]}",
                    cmp=(rt, m),
                    rng=rng,
                )
                if r.a[rt] > r.a[m]:
                    m = rt
            if m == i:
                break
            r.swap(i, m, 8, rng=rng)
            i = m

    for i in range(r.n // 2 - 1, -1, -1):
        r.emit(0, f"Build the max-heap: sift down from index {i}", cmp=(i,))
        sift(i, r.n)
    for end in range(r.n - 1, 0, -1):
        r.swap(0, end, 2, rng=(0, end))
        r.done.add(end)
        sift(0, end)
    return r.finish()


SORTS = {
    "Bubble sort": sort_bubble,
    "Selection sort": sort_selection,
    "Insertion sort": sort_insertion,
    "Merge sort": sort_merge,
    "Quick sort": sort_quick,
    "Heap sort": sort_heap,
}


def race_frames(fa, fb):
    n = max(len(fa), len(fb))
    return [
        {
            "race": (fa[min(i, len(fa) - 1)], fb[min(i, len(fb) - 1)]),
            "i": i,
            "na": len(fa),
            "nb": len(fb),
        }
        for i in range(n)
    ]
