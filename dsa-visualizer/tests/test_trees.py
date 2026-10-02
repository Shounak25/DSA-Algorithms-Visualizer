import random

import pytest

from dsa_visualizer.algorithms.trees import (
    TREE_ALGOS,
    bst_height,
    build_bst,
    make_tree_frames,
)

VALUES = [8, 3, 10, 1, 6, 14, 4, 7, 13]


def visited(frames):
    return frames[-1]["visited"]


def test_inorder_gives_sorted_keys():
    assert visited(make_tree_frames("In-order", VALUES)) == sorted(VALUES)


def test_preorder_and_postorder():
    assert visited(make_tree_frames("Pre-order", VALUES)) == [
        8,
        3,
        1,
        6,
        4,
        7,
        10,
        14,
        13,
    ]
    assert visited(make_tree_frames("Post-order", VALUES)) == [
        1,
        4,
        7,
        6,
        3,
        13,
        14,
        10,
        8,
    ]


def test_level_order():
    assert visited(make_tree_frames("Level-order", VALUES)) == [
        8,
        3,
        10,
        1,
        6,
        14,
        4,
        7,
        13,
    ]


def test_bst_height():
    assert bst_height(build_bst(VALUES)) == 4
    assert bst_height(build_bst([1, 2, 3, 4, 5])) == 5  # degenerate chain


@pytest.mark.parametrize("target", [7, 99])
def test_search_frames_end_cleanly(target):
    frames = make_tree_frames("Search (BST)", VALUES, target)
    assert frames and frames[-1]["status"]


def test_avl_stays_balanced_on_sorted_input():
    frames = make_tree_frames("AVL insert", list(range(1, 16)))
    root, kids, _ = frames[-1]["tree"]

    def height(n):
        return 0 if n is None else 1 + max(height(kids[n][0]), height(kids[n][1]))

    def balanced(n):
        if n is None:
            return True
        l, r = kids[n]
        return abs(height(l) - height(r)) <= 1 and balanced(l) and balanced(r)

    assert balanced(root)
    assert height(root) == 4  # a plain BST would be 15 deep


def test_min_heap_extract_outputs_sorted_order():
    frames = make_tree_frames(
        "Min-heap extract", random.Random(5).sample(range(50), 10)
    )
    assert "sorted order" in frames[-1]["status"]


@pytest.mark.parametrize("algo", TREE_ALGOS)
def test_every_algorithm_produces_frames(algo):
    frames = make_tree_frames(algo, VALUES, 7)
    assert len(frames) > 1
    assert all("tree" in f and "status" in f for f in frames)
