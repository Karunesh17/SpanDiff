import unittest

from spandiff.orchestration import CompareCoordinator, VariantRun


class CoordinatorTests(unittest.TestCase):
    def test_variants_run_sequentially_and_alternate_order(self):
        calls = []
        def run(variant, revision, fixture, batch):
            calls.append((variant, revision, batch))
            return VariantRun(variant, revision, fixture, batch, True, "ok")
        manifest = CompareCoordinator(run).run("base", "head", "fixture-1", repeat=2)
        self.assertEqual([call[0] for call in calls], ["baseline", "candidate", "candidate", "baseline"])
        self.assertTrue(manifest.comparable)

    def test_stage_failure_is_retained_and_incomparable(self):
        def run(variant, revision, fixture, batch):
            if variant == "candidate":
                raise RuntimeError("failure")
            return VariantRun(variant, revision, fixture, batch, True, "ok")
        manifest = CompareCoordinator(run).run("base", "head", "fixture-1")
        self.assertFalse(manifest.comparable)
        self.assertIn("stage failed", manifest.runs[1].detail)


if __name__ == "__main__":
    unittest.main()
