import importlib.util
from pathlib import Path
import sys
import unittest


MODULE = Path(__file__).parents[1] / "examples" / "fastapi-orders" / "fixture.py"
SPEC = importlib.util.spec_from_file_location("orders_fixture", MODULE)
fixture = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = fixture
SPEC.loader.exec_module(fixture)


class DemoFixtureTests(unittest.TestCase):
    def test_unchanged_is_stable_and_n_plus_one_is_detectable(self):
        baseline = fixture.run_orders("baseline")
        unchanged = fixture.run_orders("unchanged")
        candidate = fixture.run_orders("n-plus-one")
        self.assertEqual(baseline.response, unchanged.response)
        self.assertEqual(baseline.operations, unchanged.operations)
        self.assertEqual(baseline.response, candidate.response)
        self.assertEqual(baseline.query_counts.get("items.select", 0), 0)
        self.assertEqual(candidate.query_counts["items.select"], 3)
        self.assertEqual(candidate.dependency_calls, 1)

    def test_unknown_variant_fails_without_side_effects(self):
        with self.assertRaisesRegex(ValueError, "variant"):
            fixture.run_orders("production")


if __name__ == "__main__":
    unittest.main()
