from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_eta9_directed_cayley_serre_scale.packet.json"


class Q79Eta9DirectedCayleySerreScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_independent_all_row_replay(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_eta9_directed_cayley_serre_scale.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CBF.T65 verification: PASS", result.stdout)

    def test_exact_and_complex_minors_have_distinct_roles(self) -> None:
        minors = self.packet["minors"]
        self.assertEqual(minors["exact_good_reduction"]["rows"], 9360)
        self.assertEqual(minors["exact_good_reduction"]["columns"], 9360)
        self.assertEqual(minors["complex_top_anchored"]["rows"], 6777)
        self.assertEqual(minors["complex_top_anchored"]["columns"], 6777)

    def test_top_anchor_reduces_the_complex_unknowns(self) -> None:
        for row in self.packet["rows"]:
            self.assertEqual(row["critical_functional_top_anchor_rows"], 2584)
            self.assertEqual(row["critical_functional_free_coordinates"], 6777)
            self.assertLess(
                row["diagnostics"]["top_embedding_value_relative_residual"],
                1.0e-12,
            )
            self.assertLess(
                row["diagnostics"]["top_embedding_derivative_relative_residual"],
                1.0e-10,
            )

    def test_all_original_rows_are_checked(self) -> None:
        for row in self.packet["rows"]:
            self.assertEqual(row["critical_relation_nonzeros"], 1175148)
            self.assertLess(
                row["diagnostics"]["all_row_value_relative_residual"], 1.0e-8
            )
            self.assertLess(
                row["diagnostics"]["all_row_derivative_relative_residual"],
                1.0e-8,
            )

    def test_binary_scale_and_derivative_scouts_are_emitted_at_both_midpoints(self) -> None:
        self.assertEqual(
            [row["segment"] for row in self.packet["rows"]],
            ["edge-2", "edge-0"],
        )
        for row in self.packet["rows"]:
            self.assertNotEqual(row["canonical_Serre_scale"], [0.0, 0.0])
            self.assertEqual(
                len(row["canonical_Serre_scale_derivative"]), 2
            )

    def test_three_gauges_reject_binary_value_promotion(self) -> None:
        audit = self.packet["binary_row_gauge_audit"]
        self.assertEqual([row["seed"] for row in audit["rows"]], [7909, 7919, 7933])
        self.assertEqual(
            len({row["selected_rows_sha256"] for row in audit["rows"]}),
            3,
        )
        self.assertGreater(
            audit["minimum_pairwise_Serre_scale_relative_gap"],
            0.01,
        )
        self.assertFalse(audit["decision"]["binary_coefficient_scale_is_promoted"])
        self.assertFalse(
            audit["decision"]["binary_coefficient_derivative_is_promoted"]
        )
        self.assertTrue(
            audit["decision"][
                "characteristic_zero_coefficient_ball_extension_is_required"
            ]
        )

    def test_refinement_capsules_are_machine_independent(self) -> None:
        for seed in (7909, 7919, 7933):
            directory = (
                ROOT
                / "certificates"
                / f"q79_eta9_cayley_critical_refinement_seed{seed}"
            )
            metadata = json.loads((directory / "metadata.json").read_text(encoding="ascii"))
            selected = ROOT / metadata["selected_rows"]["path"]
            self.assertTrue(selected.is_file())
            self.assertTrue(selected.resolve().is_relative_to(directory.resolve()))

    def test_scope_and_parameter_ledger_are_honest(self) -> None:
        self.assertEqual(
            self.packet["status"],
            "FROZEN_BINARY_CAYLEY_SERRE_SCALE_PROMOTION_REJECTED_BY_ROW_GAUGE_TEST",
        )
        self.assertTrue(all(self.packet["checks"].values()))
        self.assertFalse(any(self.packet["guardrails"].values()))
        self.assertEqual(self.packet["parameter_ledger"]["observed_values_used"], 0)
        self.assertEqual(
            self.packet["parameter_ledger"]["new_continuous_fit_parameters"], 0
        )
        self.assertEqual(
            self.packet["parameter_ledger"]["new_discrete_fit_parameters"], 0
        )


if __name__ == "__main__":
    unittest.main()
