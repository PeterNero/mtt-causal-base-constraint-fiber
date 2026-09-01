import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "q79_b89_same_source_deligne_promote.py"
SPEC = importlib.util.spec_from_file_location("q79_b89_same_source_deligne_promote", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class SameSourceDelignePromotionTests(unittest.TestCase):
    def complete_packet(self):
        return {
            "theorem_id": "CBF.T54",
            "decision": "READY_FOR_JOINT_ASSEMBLY_AND_B89_PROMOTION",
            "coverage": {
                "branch": {"certified_intervals": 2195, "complete": True},
                "boundary": {"certified_intervals": 2195, "complete": True},
            },
            "checks": {"coverage": True},
            "guardrails": {"premature_claim": False},
        }

    def test_accepts_only_complete_exact_coverage(self):
        packet = self.complete_packet()
        self.assertTrue(MODULE.promotion_ready(packet))
        packet["coverage"]["branch"]["certified_intervals"] = 2194
        self.assertFalse(MODULE.promotion_ready(packet))

    def test_rejects_guardrail_or_wrong_decision(self):
        packet = self.complete_packet()
        packet["guardrails"]["premature_claim"] = True
        self.assertFalse(MODULE.promotion_ready(packet))
        packet = self.complete_packet()
        packet["decision"] = "STATIC_ENDPOINT_READY_BRANCH_ISOTOPY_PENDING"
        self.assertFalse(MODULE.promotion_ready(packet))


if __name__ == "__main__":
    unittest.main()
