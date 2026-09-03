from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np
from scipy import sparse


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_eta9_cayley_critical_correlated_readout.packet.json"
SIGNED = (
    ROOT
    / "certificates"
    / "q79_eta9_cayley_critical_signed_correction_seed7909"
    / "metadata.json"
)
TOP = (
    ROOT
    / "certificates"
    / "q79_eta9_cayley_top_signed_source_seed7909"
    / "metadata.json"
)


class Q79Eta9CayleyCriticalCorrelatedReadoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))
        cls.signed = json.loads(SIGNED.read_text(encoding="ascii"))
        cls.top = json.loads(TOP.read_text(encoding="ascii"))

    def test_independent_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_eta9_cayley_critical_correlated_readout.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CBF.T67 verification: PASS", result.stdout)

    def test_exact_square_zero_cayley_map(self) -> None:
        binding = self.signed["matrices"]["pivot_from_top_map"]
        cayley = sparse.load_npz(ROOT / binding["path"]).tocsr()
        identity = sparse.identity(cayley.shape[0], dtype=cayley.dtype, format="csr")
        nilpotent = (identity - cayley).tocsr()
        square = (nilpotent @ nilpotent).tocsr()
        self.assertEqual(cayley.shape, (2584, 2584))
        self.assertTrue(np.array_equal(cayley.diagonal(), np.ones(2584)))
        self.assertEqual(square.nnz, 0)

    def test_signed_top_source_removes_export_width(self) -> None:
        diagnostics = self.top["diagnostics"]
        self.assertLess(
            diagnostics["value"]["maximum_genuine_forward_tail_component"],
            2.0e-33,
        )
        self.assertLess(
            diagnostics["derivative"]["maximum_genuine_forward_tail_component"],
            2.0e-24,
        )
        self.assertLess(diagnostics["promoted_value_tail_ratio"], 1.0e-15)

    def test_denominator_and_first_jet_exclude_zero(self) -> None:
        denominator = self.packet["denominator"]
        derivative = self.packet["denominator_derivative"]
        self.assertTrue(denominator["excludes_zero"])
        self.assertTrue(derivative["excludes_zero"])
        self.assertGreater(denominator["absolute_lower"], 1.8e-4)
        self.assertGreater(derivative["absolute_lower"], 1.1e-3)

    def test_scale_is_precise_and_formula_bound(self) -> None:
        scale = self.packet["canonical_Serre_scale"]
        self.assertEqual(scale["formula"], "585/(2D)")
        self.assertLess(scale["value_disk"]["relative_error_upper"], 1.0e-15)
        self.assertLess(scale["derivative_disk"]["absolute_error"], 1.1e-3)

    def test_all_relation_rows_are_inherited(self) -> None:
        checks = self.packet["checks"]
        self.assertTrue(
            checks["the_T66_characteristic_zero_inverse_certificate_is_inherited"]
        )
        self.assertEqual(self.packet["dimensions"]["critical_functional"], 9361)
        self.assertEqual(self.packet["dimensions"]["balanced_system"], 6777)
        self.assertEqual(self.packet["dimensions"]["common_anchor_source"], 2584)

    def test_scope_and_parameter_ledger(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["observed_values_used"], 0)
        self.assertEqual(ledger["new_continuous_fit_parameters"], 0)
        self.assertEqual(ledger["new_discrete_fit_parameters"], 0)
        self.assertFalse(self.packet["guardrails"]["physical_endpoint_selected_here"])
        self.assertIn(
            "selection of the q79 physical HYM endpoint",
            self.packet["guardrails"]["not_claimed"],
        )


if __name__ == "__main__":
    unittest.main()
