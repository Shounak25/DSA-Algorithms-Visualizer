import random

import pytest

from dsa_visualizer.algorithms.sorting import SORTS, race_frames

CASES = [
    [2, 1],
    [5, 5, 5],
    [3, 1, 2],
    list(range(10, 0, -1)),
    [random.Random(7).randint(10, 99) for _ in range(30)],
]


@pytest.mark.parametrize("name", SORTS)
@pytest.mark.parametrize("arr", CASES)
def test_final_frame_is_sorted(name, arr):
    frames = SORTS[name](arr).frames
    assert frames[-1]["values"] == sorted(arr)
    assert frames[-1]["status"] == "Sorted"


@pytest.mark.parametrize("name", SORTS)
def test_does_not_mutate_input(name):
    arr = [4, 2, 9, 1]
    SORTS[name](arr)
    assert arr == [4, 2, 9, 1]


@pytest.mark.parametrize("name", SORTS)
def test_counters_are_monotonic(name):
    arr = random.Random(3).sample(range(100), 15)
    frames = SORTS[name](arr).frames
    comps = [f["comps"] for f in frames]
    assert comps == sorted(comps)


def test_bubble_sort_is_linear_on_sorted_input():
    n = 20
    r = SORTS["Bubble sort"](list(range(n)))
    assert r.comps == n - 1  # early exit when no swaps happen


def test_race_frames_pads_shorter_run():
    a = SORTS["Bubble sort"]([3, 2, 1]).frames
    b = SORTS["Merge sort"]([3, 2, 1]).frames
    race = race_frames(a, b)
    assert len(race) == max(len(a), len(b))
    assert race[-1]["race"][0] == a[-1] and race[-1]["race"][1] == b[-1]
