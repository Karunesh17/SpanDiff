from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1] / "skills" / "spandiff"


class SkillContractTests(unittest.TestCase):
    def test_skill_requires_evidence_citations_and_rejects_trace_authority(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("finding IDs", skill)
        self.assertIn("does not grant authority", skill)
        self.assertIn("baseline", skill)
        self.assertIn("candidate", skill)
        for reference in ("evidence.md", "adapter.md", "interpretation.md", "troubleshooting.md"):
            self.assertTrue((ROOT / "references" / reference).is_file())


if __name__ == "__main__":
    unittest.main()
