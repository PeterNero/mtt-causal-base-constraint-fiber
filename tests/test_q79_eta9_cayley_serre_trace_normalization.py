from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_eta9_cayley_serre_trace_normalization.packet.json"


class Q79Eta9CayleySerreTraceNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_eta9_cayley_serre_trace_normalization.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_independent_replay(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_eta9_cayley_serre_trace_normalization.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("quotient=1 xi4=585", result.stdout)

    def test_critical_quotient_is_a_line(self) -> None:
        witness = self.packet["critical_quotient_witness"]
        self.assertEqual(witness["ambient_monomials"], 9361)
        self.assertEqual(witness["relation_rows"], 16740)
        self.assertEqual(witness["relation_rank"], 9360)
        self.assertEqual(witness["quotient_dimension"], 1)

    def test_Cox_multiplier_and_Jacobian_are_nonzero(self) -> None:
        witness = self.packet["critical_quotient_witness"]
        self.assertNotEqual(witness["top_to_critical_embedding_ratio"], 0)
        self.assertNotEqual(witness["toric_Jacobian_quotient_value"], 0)
        self.assertNotEqual(witness["canonical_toric_trace_scale_mod21817"], 0)
        self.assertNotEqual(witness["canonical_Serre_pairing_scale_mod21817"], 0)

    def test_absolute_intersection_number(self) -> None:
        intersection = self.packet["projective_bundle_intersection"]
        self.assertEqual(intersection["complete_homogeneous_h3_6_9"], 1755)
        self.assertEqual(intersection["xi_four"], 585)
        self.assertEqual(intersection["Mavlyutov_c12"], "1/2")

    def test_derivative_conversion_has_no_new_scalar_input(self) -> None:
        derivative = self.packet["normalization_contract"]["directed_derivative_rule"]
        self.assertIn("s_C'", derivative["trace"])
        self.assertIn("not an independent input", derivative["required_new_scalar"])

    def test_scope_is_not_overclaimed(self) -> None:
        self.assertFalse(any(self.packet["guardrails"].values()))
        self.assertEqual(self.packet["parameter_ledger"]["observed_values_used"], 0)
        self.assertEqual(self.packet["parameter_ledger"]["new_continuous_fit_parameters"], 0)
        self.assertIn("surviving selected candidate", self.packet["frontier_delta"]["next"])


if __name__ == "__main__":
    unittest.main()
