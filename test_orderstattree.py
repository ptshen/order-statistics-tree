"""Regression and model-based tests for the adjacent main.py.

Run: python3 test_orderstattree.py
Verbose: python3 test_orderstattree.py -v
Discovery: python3 -m unittest discover -v

Contract under test:
* Every insertion adds one node, including duplicate values.
* Left descendants are <= their ancestor; right descendants are > it.
* length counts all nodes; num_below counts a node and all its descendants.
* For 0 <= p <= 1, percentile returns sorted_values[max(1, floor(p*n))-1].
  This follows main.py's existing floor-based convention, without interpolation.
* Percentiles of an empty tree return None; queries do not mutate the tree.

Out-of-range p, NaN, and incomparable values are excluded: main.py does not
currently specify their behavior. Random tests use fixed seeds for repeatability.
Each named test counts once in the summary, even if it checks many operations.
"""

import itertools
import math
import random
import unittest
from fractions import Fraction

from main import OrderStatisticsTree, TreeNode


def reference_percentile(values, p):
    """Independent sorted-list oracle; never consult tree metadata."""
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.floor(p * len(ordered)) - 1)
    return ordered[index]


def fixture_tree(shape):
    """Build explicit, valid query fixtures without calling insert.

    A scalar is a leaf, None is empty, and (value, left, right) is a branch.
    This lets percentile tests run even when insertion is broken.
    """
    def build(spec):
        if spec is None:
            return None, []
        if not isinstance(spec, tuple):
            return TreeNode(spec), [spec]
        value, left_spec, right_spec = spec
        left, left_values = build(left_spec)
        right, right_values = build(right_spec)
        values = left_values + [value] + right_values
        return TreeNode(value, left, right, len(values)), values

    tree = OrderStatisticsTree()
    tree.root, values = build(shape)
    tree.length = len(values)
    return tree, values


class TreeAssertions(unittest.TestCase):
    def assert_tree_matches(self, tree, values, context=""):
        """Check global ordering, node identity, contents, and every count.

        Traversals are iterative so deep, unbalanced trees are supported.
        Detect cycles/shared children before starting the other traversals.
        """
        self.assertEqual(tree.length, len(values), f"{context}: length")
        if not values:
            self.assertIsNone(tree.root, f"{context}: empty root")
            return
        self.assertIsNotNone(tree.root, f"{context}: missing root")

        seen = set()
        nodes = []
        stack = [(tree.root, None, None)]
        while stack:
            node, lower, upper = stack.pop()
            self.assertNotIn(id(node), seen, f"{context}: cycle/shared child")
            seen.add(id(node))
            nodes.append(node)
            if lower is not None:
                self.assertGreater(node.value, lower,
                                   f"{context}: right-subtree ancestor bound")
            if upper is not None:
                self.assertLessEqual(node.value, upper,
                                     f"{context}: left-subtree ancestor bound")
            if node.left is not None:
                stack.append((node.left, lower, node.value))
            if node.right is not None:
                stack.append((node.right, node.value, upper))
        self.assertEqual(len(nodes), len(values), f"{context}: reachable nodes")

        sizes = {}
        for node in reversed(nodes):
            actual = 1 + sizes.get(id(node.left), 0) + sizes.get(id(node.right), 0)
            self.assertEqual(node.num_below, actual,
                             f"{context}: num_below at value {node.value!r}")
            sizes[id(node)] = actual

        ordered = []
        stack = []
        node = tree.root
        while node is not None or stack:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            ordered.append(node.value)
            node = node.right
        self.assertEqual(ordered, sorted(values), f"{context}: sorted contents")

    def snapshot(self, tree):
        """Record identities, links, values and counts to detect query mutation."""
        state = []
        stack = [tree.root] if tree.root is not None else []
        seen = set()
        while stack:
            node = stack.pop()
            self.assertNotIn(id(node), seen, "cycle/shared child in snapshot")
            seen.add(id(node))
            state.append((id(node), node.value, id(node.left), id(node.right),
                          node.num_below))
            if node.left is not None:
                stack.append(node.left)
            if node.right is not None:
                stack.append(node.right)
        return id(tree.root), tree.length, tuple(state)

    def assert_percentiles(self, tree, values, percentiles, context=""):
        before = self.snapshot(tree)
        for p in percentiles:
            self.assertEqual(tree.p_percentile(p), reference_percentile(values, p),
                             f"{context}: p={p!r}, n={len(values)}")
        self.assertEqual(self.snapshot(tree), before,
                         f"{context}: percentile query mutated tree")

    def assert_every_rank(self, tree, values, context=""):
        percentiles = [0, 0.01, 0.25, 0.5, 0.75, 0.99, 1]
        n = len(values)
        if n:
            for rank in range(1, n + 1):
                # Exact boundaries avoid accidental floating-point rounding.
                percentiles.append(Fraction(rank, n))
                if rank < n:
                    percentiles.append(Fraction(2 * rank + 1, 2 * n))
        self.assert_percentiles(tree, values, percentiles, context)


class NodeTests(unittest.TestCase):
    def test_defaults(self):
        node = TreeNode(42)
        self.assertEqual(node.value, 42)
        self.assertIsNone(node.left)
        self.assertIsNone(node.right)
        self.assertEqual(node.num_below, 1)

    def test_constructor_preserves_children_and_count(self):
        left, right = TreeNode(1), TreeNode(3)
        node = TreeNode(2, left, right, num_below=3)
        self.assertEqual(node.value, 2)
        self.assertIs(node.left, left)
        self.assertIs(node.right, right)
        self.assertEqual(node.num_below, 3)

    def test_nodes_have_independent_state(self):
        first, second = TreeNode(1), TreeNode(1)
        first.left = TreeNode(0)
        first.num_below = 2
        self.assertIsNone(second.left)
        self.assertEqual(second.num_below, 1)


class InsertionTests(TreeAssertions):
    def test_empty_tree(self):
        self.assert_tree_matches(OrderStatisticsTree(), [])

    def test_first_insert_creates_root(self):
        tree = OrderStatisticsTree()
        tree.insert(42)
        self.assertIsNotNone(tree.root)
        self.assertEqual(tree.root.value, 42)
        self.assertIsNone(tree.root.left)
        self.assertIsNone(tree.root.right)

    def test_first_insert_updates_length(self):
        tree = OrderStatisticsTree()
        tree.insert(42)
        self.assertEqual(tree.length, 1)

    def test_first_insert_sets_subtree_count(self):
        tree = OrderStatisticsTree()
        tree.insert(42)
        self.assertEqual(tree.root.num_below, 1)

    def test_equal_value_goes_left(self):
        tree = OrderStatisticsTree()
        tree.insert(5)
        original_root = tree.root
        tree.insert(5)
        self.assertIs(tree.root, original_root)
        self.assertIsNotNone(tree.root.left)
        self.assertEqual(tree.root.left.value, 5)
        self.assertIsNot(tree.root.left, tree.root)
        self.assertIsNone(tree.root.right)

    def test_left_insertion_updates_root_count(self):
        tree = OrderStatisticsTree()
        tree.insert(10)
        tree.insert(5)
        self.assertEqual(tree.root.num_below, 2)

    def test_right_insertion_updates_root_count(self):
        tree = OrderStatisticsTree()
        tree.insert(10)
        tree.insert(15)
        self.assertEqual(tree.root.num_below, 2)

    def test_tree_instances_are_independent(self):
        first, second = OrderStatisticsTree(), OrderStatisticsTree()
        first.insert(10)
        self.assert_tree_matches(second, [])
        second.insert(-10)
        self.assertIsNot(first.root, second.root)
        self.assertEqual(first.root.value, 10)
        self.assertEqual(second.root.value, -10)

    def check_sequence(self, values):
        tree = OrderStatisticsTree()
        inserted = []
        for step, value in enumerate(values, 1):
            tree.insert(value)
            inserted.append(value)
            self.assert_tree_matches(tree, inserted, f"insertion {step}: {value!r}")
        self.assert_every_rank(tree, inserted)


INSERTION_CASES = {
    "two_values_left": [2, 1],
    "two_values_right": [1, 2],
    "ascending": list(range(40)),
    "descending": list(range(40, 0, -1)),
    "balanced_order": [8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7, 9, 11, 13, 15],
    "zigzag": [50, 10, 40, 20, 30, 90, 60, 80, 70],
    "all_equal": [7] * 30,
    "duplicates_across_levels": [5, 3, 7, 5, 3, 7, 5, 2, 8, 2, 8, 5],
    "negative_and_zero": [0, -1, -100, 1, 100, -1, 0],
    "large_integers": [0, 10**100, -(10**100), 10**100 + 1, -(10**100) + 1],
    "floats": [0.0, -2.5, 3.25, 0.125, -2.5, 1.5, -0.0],
    "mixed_ints_and_floats": [2, 2.0, 1.5, -1, -1.0, 0, 3.5],
    "strings": ["pear", "apple", "orange", "banana", "apple", ""],
}


def insertion_case(values):
    def test(self):
        self.check_sequence(values)
    return test


for case_name, case_values in INSERTION_CASES.items():
    setattr(InsertionTests, f"test_sequence_{case_name}", insertion_case(case_values))


QUERY_FIXTURES = {
    "empty": None,
    "singleton": 42,
    "two_nodes_left": (20, 10, None),
    "two_nodes_right": (10, None, 20),
    "balanced": (4, (2, 1, 3), (6, 5, 7)),
    "uneven": (10, (2, 1, (8, (6, 4, 7), 9)), (20, None, 30)),
    "left_chain": (5, (4, (3, (2, 1, None), None), None), None),
    "right_chain": (1, None, (2, None, (3, None, (4, None, 5)))),
    "duplicates": (5, (5, (3, 3, 4), None), (8, (7, 7, None), 9)),
    "all_equal": (5, (5, (5, 5, None), None), None),
    "negative_and_zero": (0, (-3, -5, -1), (3, 1, 5)),
    "floats": (0.5, (-1.25, -2.5, 0.0), (2.75, 1.5, 4.125)),
    "strings": ("mango", ("banana", "apple", "kiwi"), ("pear", None, "plum")),
}


class PercentileTests(TreeAssertions):
    def test_single_insert_all_percentiles(self):
        tree = OrderStatisticsTree()
        tree.insert(42)
        self.assert_every_rank(tree, [42])

    def test_floor_rank_convention(self):
        tree, _ = fixture_tree((30, (20, 10, None), 40))
        # Explicit examples pin down the oracle's convention too.
        for p, expected in [(0, 10), (0.24, 10), (0.25, 10), (0.49, 10),
                            (0.5, 20), (0.74, 20), (0.75, 30), (0.99, 30),
                            (1, 40)]:
            self.assertEqual(tree.p_percentile(p), expected, f"p={p}")

    def test_float_neighbors_of_rank_boundaries(self):
        tree, values = fixture_tree(QUERY_FIXTURES["uneven"])
        percentiles = [math.nextafter(0.0, 1.0), math.nextafter(1.0, 0.0)]
        for rank in range(1, len(values)):
            p = rank / len(values)
            percentiles.extend([math.nextafter(p, 0.0), p, math.nextafter(p, 1.0)])
        self.assert_percentiles(tree, values, percentiles)

    def test_repeated_queries_in_arbitrary_order(self):
        tree, values = fixture_tree(QUERY_FIXTURES["balanced"])
        rng = random.Random(314159)
        percentiles = [rng.random() for _ in range(300)] + [1, 0, 1, 0, 0.5] * 10
        self.assert_percentiles(tree, values, percentiles)

    def test_deep_left_query_fixture(self):
        self.check_deep_fixture(left=True)

    def test_deep_right_query_fixture(self):
        self.check_deep_fixture(left=False)

    def check_deep_fixture(self, left):
        tree = OrderStatisticsTree()
        n = 1500
        values = range(n) if left else reversed(range(n))
        for size, value in enumerate(values, 1):
            tree.root = TreeNode(value, tree.root if left else None,
                                 None if left else tree.root, size)
        tree.length = n
        expected = list(range(n))
        self.assert_tree_matches(tree, expected)
        self.assert_percentiles(tree, expected, [0, 0.001, 0.25, 0.5, 0.9, 0.999, 1])


def query_case(shape):
    def test(self):
        tree, values = fixture_tree(shape)
        self.assert_tree_matches(tree, values, "query fixture")
        self.assert_every_rank(tree, values)
    return test


for case_name, case_shape in QUERY_FIXTURES.items():
    setattr(PercentileTests, f"test_fixture_{case_name}", query_case(case_shape))


class ModelTests(TreeAssertions):
    def test_all_insertion_orders_of_five_distinct_values(self):
        for order in itertools.permutations([-2, -1, 0, 1, 2]):
            tree = OrderStatisticsTree()
            inserted = []
            for value in order:
                tree.insert(value)
                inserted.append(value)
                self.assert_tree_matches(tree, inserted, f"order={order}")
                self.assert_every_rank(tree, inserted, f"order={order}")

    def test_all_insertion_orders_with_duplicates(self):
        for order in sorted(set(itertools.permutations([0, 0, 1, 1, 2]))):
            tree = OrderStatisticsTree()
            inserted = []
            for value in order:
                tree.insert(value)
                inserted.append(value)
                self.assert_tree_matches(tree, inserted, f"order={order}")
                self.assert_every_rank(tree, inserted, f"order={order}")

    def test_long_ascending_insertions(self):
        self.check_long_sequence(list(range(1500)))

    def test_long_descending_insertions(self):
        self.check_long_sequence(list(range(1499, -1, -1)))

    def test_long_duplicate_sequence(self):
        self.check_long_sequence([5] * 1500)

    def check_long_sequence(self, values):
        tree = OrderStatisticsTree()
        for value in values:
            tree.insert(value)
        self.assert_tree_matches(tree, values)
        self.assert_percentiles(tree, values, [0, 0.001, 0.1, 0.5, 0.9, 0.999, 1])

    def check_random_sequence(self, seed):
        rng = random.Random(seed)
        tree = OrderStatisticsTree()
        values = []
        self.assert_every_rank(tree, values, f"seed={seed}, initially empty")
        for step in range(120):
            # Alternate a duplicate-heavy range with a much wider value range.
            value = rng.randint(-8, 8) if step % 2 else rng.randint(-10**6, 10**6)
            tree.insert(value)
            values.append(value)
            context = f"seed={seed}, step={step}, inserted={value}"
            self.assert_tree_matches(tree, values, context)
            self.assert_percentiles(tree, values,
                                    [0, 1, 0.5] + [rng.random() for _ in range(5)],
                                    context)
        self.assert_every_rank(tree, values, f"seed={seed}, final state")


def random_case(seed):
    def test(self):
        self.check_random_sequence(seed)
    return test


for seed in [0, 1, 2, 3, 4, 5, 17, 42, 2026, 8675309]:
    setattr(ModelTests, f"test_random_seed_{seed}", random_case(seed))


class SummaryRunner(unittest.TextTestRunner):
    def run(self, test):
        result = super().run(test)
        failed = len(result.failures)
        errors = len(result.errors)
        skipped = len(result.skipped)
        passed = result.testsRun - failed - errors - skipped
        self.stream.writeln(
            f"\nSummary: {passed} passed | {failed} failed | {errors} errors | "
            f"{skipped} skipped | {result.testsRun} total"
        )
        return result


if __name__ == "__main__":
    unittest.main(testRunner=SummaryRunner)
