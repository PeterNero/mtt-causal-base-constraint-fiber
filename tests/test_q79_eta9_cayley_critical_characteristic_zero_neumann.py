from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_eta9_cayley_critical_characteristic_zero_neumann.packet.json"
INPUT = (
    ROOT
    / "certificates"
    / "q79_eta9_cayley_critical_characteristic_zero_seed7909"
    / "metadata.json"
)


class Q79Eta9CayleyCriticalCharacteristicZeroTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))
        cls.input = json.loads(INPUT.read_text(encoding="ascii"))

    def test_independent_verifier(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "verify_q79_eta9_cayley_critical_characteristic_zero_neumann.py",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CBF.T66 verification: PASS", result.stdout)

    def test_exact_input_dimensions_and_embedding(self) -> None:
        self.assertEqual(self.input["dimensions"]["critical_basis"], 9361)
        self.assertEqual(self.input["dimensions"]["top_anchor"], 2584)
        self.assertEqual(self.input["dimensions"]["free_coordinates"], 6777)
        self.assertEqual(self.input["dimensions"]["nonzero_reduced_rows"], 13014)
        self.assertEqual(self.input["top_embedding"]["nilpotence_index"], 2)

    def test_neumann_decision_is_honest(self) -> None:
        eta = self.packet["inverse_certificate"]["maximum_total_Neumann_row"]
        if self.packet["status"] == "SEED7909_CHARACTERISTIC_ZERO_NEUMANN_INVERSE_REJECTED":
            self.assertGreaterEqual(eta, 1.0)
            self.assertNotIn("all_row_audit", self.packet)
        else:
            self.assertLess(eta, 1.0)
            self.assertIn("all_row_audit", self.packet)

    def test_only_coarse_failing_rows_are_replaced_by_Arb_bounds(self) -> None:
        refinement = self.packet["targeted_high_precision_refinement"]
        coarse = np.load(ROOT / refinement["coarse_Neumann_row_bounds"]["path"])
        rows = np.load(ROOT / refinement["row_indices"]["path"])
        totals = np.load(ROOT / refinement["total_bounds"]["path"])
        final = np.load(ROOT / self.packet["Neumann_row_bounds"]["path"])
        self.assertTrue(np.array_equal(rows, np.flatnonzero(coarse >= 1.0)))
        reconstructed = coarse.copy()
        reconstructed[rows] = totals
        self.assertTrue(np.array_equal(reconstructed, final))

    def test_no_interval_containing_zero_is_inverted(self) -> None:
        if "toric_Jacobian" not in self.packet:
            return
        excludes_zero = self.packet["toric_Jacobian"]["excludes_zero"]
        emitted = self.packet["canonical_Serre_scale"]["value_ball"] is not None
        self.assertEqual(excludes_zero, emitted)

    def test_scope_and_parameter_ledger(self) -> None:
        self.assertFalse(any(self.packet["guardrails"].values()))
        ledger = self.packet.get("parameter_ledger", {})
        if ledger:
            self.assertEqual(ledger["observed_values_used"], 0)
            self.assertEqual(ledger["new_continuous_fit_parameters"], 0)
            self.assertEqual(ledger["new_discrete_fit_parameters"], 0)
        self.assertTrue(self.input["checks"]["no_observed_value_or_fit_parameter_is_used"])


if __name__ == "__main__":
    unittest.main()
