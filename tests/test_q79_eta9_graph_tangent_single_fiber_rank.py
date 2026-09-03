from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_eta9_graph_tangent_single_fiber_rank.packet.json"


class Q79Eta9GraphTangentSingleFiberRankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_eta9_graph_tangent_single_fiber_rank.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_independent_kernel_first_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_eta9_graph_tangent_single_fiber_rank.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CBF.T70 verification: PASS", result.stdout)

    def test_full_graph_tangent_ranks(self) -> None:
        ranks = self.packet["rank_calculation"]
        self.assertEqual(ranks["restriction_image_on_graph_kernel_rank"], 70)
        self.assertEqual(ranks["projective_invisible_tangent_rank"], 52)
        self.assertEqual(ranks["fixed_fiber_cokernel_rank"], 12)

    def test_full_tangent_improves_the_principal_slice(self) -> None:
        ranks = self.packet["rank_calculation"]
        self.assertEqual(ranks["principal33_slice_image_rank"], 11)
        self.assertEqual(
            ranks["additional89_directions_new_image_rank_modulo_principal_image"],
            59,
        )

    def test_coefficient_result_is_not_promoted_to_normal_function(self) -> None:
        self.assertIn("BHT handle integral", self.packet["frontier_delta"]["not_closed"])
        self.assertFalse(self.packet["guardrails"]["claims_this_is_the_Abel_Jacobi_derivative"])
        self.assertFalse(self.packet["guardrails"]["claims_this_is_the_Deligne_or_BHT_derivative"])

    def test_no_parameters_or_observed_values(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["observed_values_used"], 0)
        self.assertEqual(ledger["new_continuous_fit_parameters"], 0)
        self.assertEqual(ledger["new_discrete_fit_parameters"], 0)


if __name__ == "__main__":
    unittest.main()
