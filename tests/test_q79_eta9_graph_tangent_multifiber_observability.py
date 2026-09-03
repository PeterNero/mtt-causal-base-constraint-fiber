from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_eta9_graph_tangent_multifiber_observability.packet.json"


class Q79Eta9GraphTangentMultifiberObservabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_eta9_graph_tangent_multifiber_observability.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_independent_stacked_map_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_eta9_graph_tangent_multifiber_observability.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CBF.T71 verification: PASS", result.stdout)

    def test_every_pair_leaves_eleven_directions(self) -> None:
        panel = self.packet["rank_panel"]
        self.assertEqual(set(panel["all_pair_image_ranks"].values()), {111})
        self.assertEqual(panel["all_pair_projective_kernel_rank"], 11)

    def test_dependent_third_evaluation_adds_nothing(self) -> None:
        triple = self.packet["rank_panel"]["dependent_triple"]
        self.assertEqual(triple["elliptic_weight_span_rank"], 2)
        self.assertEqual(triple["image_rank"], 111)
        self.assertEqual(triple["projective_kernel_rank"], 11)

    def test_independent_third_evaluation_is_projectively_injective(self) -> None:
        triple = self.packet["rank_panel"]["independent_triple"]
        self.assertEqual(triple["elliptic_weight_span_rank"], 3)
        self.assertEqual(triple["image_rank"], 122)
        self.assertEqual(triple["affine_common_kernel_rank"], 1)
        self.assertEqual(triple["projective_kernel_rank"], 0)
        self.assertTrue(triple["projectively_injective"])

    def test_physical_promotion_is_guarded(self) -> None:
        self.assertFalse(self.packet["guardrails"]["claims_e1_or_e3_is_a_certified_smooth_physical_fiber"])
        self.assertFalse(self.packet["guardrails"]["claims_Picard_or_normal_function_derivative_rank122"])
        self.assertFalse(self.packet["guardrails"]["claims_beta_C_is_computed"])


if __name__ == "__main__":
    unittest.main()
