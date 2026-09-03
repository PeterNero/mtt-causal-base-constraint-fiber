from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from flint import arb


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_eta9_physical_midpoint_three_evaluation_frame.packet.json"


class Q79Eta9PhysicalMidpointThreeEvaluationFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_eta9_physical_midpoint_three_evaluation_frame.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_independent_replay(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_eta9_physical_midpoint_three_evaluation_frame.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CBF.T72 verification: PASS", result.stdout)

    def test_physical_three_row_rank_is_exactly_122(self) -> None:
        rank = self.packet["characteristic_zero_rank"]
        self.assertEqual(rank["affine_graph_tangent_rank"], 123)
        self.assertEqual(rank["radial_kernel_rank"], 1)
        self.assertEqual(rank["joined_evaluation_image_rank"], 122)
        self.assertEqual(rank["projective_kernel_rank"], 0)

    def test_rows_are_actual_physical_midpoints(self) -> None:
        frame = self.packet["physical_frame"]
        self.assertEqual(frame["segments"], ["edge-0", "edge-1", "edge-2"])
        self.assertEqual(set(frame["midpoint_root_counts"].values()), {198})
        self.assertGreater(arb(frame["midpoint_weight_determinant_absolute_lower"]), 0)

    def test_positive_width_neumann_certificate(self) -> None:
        panel = self.packet["positive_width_operator_panel"]
        self.assertTrue(panel["cartesian_product_of_three_independent_parameter_boxes"])
        self.assertTrue(panel["strictly_below_one"])
        self.assertLess(arb(panel["Neumann_infinity_norm_defect_upper"]), 1)

    def test_transport_claims_remain_guarded(self) -> None:
        self.assertFalse(any(self.packet["guardrails"].values()))
        self.assertEqual(self.packet["parameter_ledger"]["observed_values_used"], 0)
        self.assertEqual(self.packet["parameter_ledger"]["new_continuous_fit_parameters"], 0)


if __name__ == "__main__":
    unittest.main()
