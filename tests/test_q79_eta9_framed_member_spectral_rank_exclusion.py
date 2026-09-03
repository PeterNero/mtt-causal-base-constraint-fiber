from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_eta9_framed_member_spectral_rank_exclusion.packet.json"


class Q79Eta9FramedMemberSpectralRankScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_eta9_framed_member_spectral_rank_exclusion.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_independent_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_eta9_framed_member_spectral_rank_exclusion.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CBF.T69 verification: PASS", result.stdout)

    def test_carriers_are_distinct(self) -> None:
        ledger = self.packet["carrier_ledger"]
        self.assertEqual(ledger["fixed_fiber_picard_point"]["holomorphic_row_rank"], 82)
        self.assertEqual(ledger["global_BHT_class"]["primitive_surface_row_rank"], 248)
        self.assertEqual(ledger["evaluation_quotient"]["kernel_rank"], 166)

    def test_fixed_fiber_result_is_retained(self) -> None:
        correction = self.packet["correction"]
        self.assertIn("1<=n<=1449", correction["retained_H4_T132_result"])
        self.assertIn("does not imply", correction["invalid_inference_removed"])

    def test_spectral_ranks_are_reopened(self) -> None:
        decision = self.packet["spectral_rank_decision"]
        self.assertEqual(
            decision["ranks_1_through_1449"],
            "UNDECIDED_BY_THE_FIXED_FIBER_CALCULATION",
        )
        self.assertEqual(decision["selected_spectral_rank_one"], "OPEN")
        self.assertEqual(decision["selected_inverse_transform_rank_three"], "OPEN")

    def test_global_bht_sweep_is_next(self) -> None:
        frontier = self.packet["frontier_delta"]
        self.assertIn("Gauss-Manin", frontier["next_required_object"])
        self.assertEqual(len(frontier["execution_order"]), 4)

    def test_no_parameters_or_observations(self) -> None:
        self.assertEqual(
            self.packet["parameter_ledger"],
            {
                "new_continuous_fit_parameters": 0,
                "new_discrete_fit_parameters": 0,
                "observed_values_used": 0,
            },
        )


if __name__ == "__main__":
    unittest.main()
