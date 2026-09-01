from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "full_graded_augmented_heterotic_symbol_parametrix.packet.json"


class FullGradedAugmentedHeteroticSymbolParametrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_full_graded_augmented_heterotic_symbol_parametrix.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))

    def test_builder_passes(self) -> None:
        self.assertEqual(self.packet["check_summary"]["total"], 45)
        self.assertTrue(self.packet["check_summary"]["all_passed"])

    def test_independent_verifier_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_full_graded_augmented_heterotic_symbol_parametrix.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn('"all_passed": true', result.stdout)
        self.assertIn('"total": 42', result.stdout)

    def test_complete_mapping_cone_has_five_degrees(self) -> None:
        theorem = self.packet["full_graded_theorem"]
        self.assertEqual(theorem["degrees"], [-1, 0, 1, 2, 3])
        self.assertTrue(theorem["degree_minus_one_scalar_completion_is_required"])

    def test_projector_ranks_are_pascal_row(self) -> None:
        theorem = self.packet["full_graded_theorem"]
        self.assertEqual(theorem["correction_ranks"], [1, 4, 6, 4, 1])

    def test_all_exact_witness_records_pass(self) -> None:
        witness = self.packet["exact_non_diagonal_witness"]
        self.assertEqual(witness["record_count"], 105)
        self.assertTrue(witness["all_projectors_exact"])
        self.assertTrue(witness["all_projector_ranks_exact"])
        self.assertTrue(witness["all_two_level_identities_exact"])

    def test_all_symbol_inverses_and_determinants_are_exact(self) -> None:
        witness = self.packet["exact_non_diagonal_witness"]
        self.assertTrue(witness["all_symbol_inverses_exact"])
        self.assertTrue(witness["all_determinants_exact"])

    def test_degree_one_replays_T57(self) -> None:
        witness = self.packet["exact_non_diagonal_witness"]
        self.assertTrue(witness["degree_one_hashes_match_T57"])

    def test_truncated_degree_zero_fails_uniform_projector_form(self) -> None:
        witness = self.packet["exact_non_diagonal_witness"]
        self.assertTrue(witness["all_truncated_degree_zero_simple_projector_controls_fail"])

    def test_witness_degree_data_are_exact(self) -> None:
        rows = self.packet["exact_non_diagonal_witness"]["degree_rows"]
        self.assertEqual([row["carrier_dimension"] for row in rows], [1, 7, 15, 13, 4])
        self.assertEqual([row["baseline_multiplicity"] for row in rows], [0, 3, 9, 9, 3])
        self.assertEqual(
            [Fraction(row["normalized_trace_factor_rho_one"]) for row in rows],
            [Fraction(5, 4), Fraction(8, 7), Fraction(11, 10), Fraction(14, 13), Fraction(17, 16)],
        )

    def test_q79_rank102_degree_data_are_exact(self) -> None:
        q79 = self.packet["q79_rank102_specialization"]
        rows = q79["degree_rows"]
        self.assertEqual([row["carrier_dimension"] for row in rows], [1, 105, 309, 307, 102])
        self.assertEqual([row["correction_rank"] for row in rows], [1, 4, 6, 4, 1])
        self.assertEqual([row["baseline_multiplicity"] for row in rows], [0, 101, 303, 303, 101])

    def test_leading_heat_supertrace_cancels(self) -> None:
        heat = self.packet["heat_supertrace_certificate"]
        self.assertEqual(heat["correction_rank_alternating_sum"], 0)
        self.assertEqual(heat["baseline_multiplicity_alternating_sum"], 0)
        self.assertEqual(Fraction(heat["witness_rho_one_heat_weight_alternating_sum"]), 0)
        self.assertEqual(Fraction(heat["q79_rho_one_heat_weight_alternating_sum"]), 0)
        self.assertFalse(heat["index_claimed"])

    def test_principal_preconditioner_is_complete_but_global_inverse_is_open(self) -> None:
        contract = self.packet["operator_execution_contract_update"]
        self.assertTrue(contract["principal_symbol_preconditioner_complete_all_degrees"])
        self.assertEqual(contract["independent_principal_symbol_inverse_rows_remaining"], 0)
        self.assertEqual(contract["selected_global_reduced_inverse"], "OPEN")
        self.assertEqual(contract["selected_inverse_tail_bounds"], "OPEN")
        self.assertFalse(contract["B_OP_01_closed"])

    def test_no_physical_parameters_or_values_are_added(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["continuous_physical_parameters_added"], 0)
        self.assertEqual(ledger["discrete_selectors_added"], 0)
        self.assertEqual(ledger["observed_values_used"], 0)
        self.assertEqual(ledger["fitted_values_used"], 0)

    def test_physical_boundary_does_not_move(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertFalse(boundary["B_GEO_01_closed"])
        self.assertFalse(boundary["B_OP_01_closed"])
        self.assertEqual(boundary["physical_gates"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_packets"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_rows"], {"accepted": 0, "total": 7})


if __name__ == "__main__":
    unittest.main()
