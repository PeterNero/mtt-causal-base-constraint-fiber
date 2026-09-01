from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "augmented_hodge_lower_order_inverse_tail_compiler.packet.json"


class AugmentedHodgeLowerOrderInverseTailCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_augmented_hodge_lower_order_inverse_tail_compiler.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_builder_passes_all_checks(self) -> None:
        summary = self.packet["check_summary"]
        self.assertTrue(summary["all_passed"])
        self.assertEqual(summary["total"], 30)

    def test_independent_verifier_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_augmented_hodge_lower_order_inverse_tail_compiler.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn('"all_passed": true', result.stdout)
        self.assertIn('"total": 27', result.stdout)

    def test_all_five_degrees_are_compiled(self) -> None:
        witness = self.packet["five_degree_exact_witness"]
        rows = witness["degree_rows"]
        self.assertEqual([row["degree"] for row in rows], [-1, 0, 1, 2, 3])
        self.assertEqual([row["carrier_dimension"] for row in rows], [1, 7, 15, 13, 4])
        self.assertEqual([row["correction_rank"] for row in rows], [1, 4, 6, 4, 1])

    def test_nonconstant_weighted_coefficient_identity_is_exact(self) -> None:
        witness = self.packet["five_degree_exact_witness"]
        self.assertEqual(witness["density_log_derivative"], "1/3")
        self.assertTrue(witness["nonconstant_principal_and_zero_order_coefficients"])
        self.assertTrue(witness["all_cochain_compositions_zero"])
        self.assertEqual(witness["cochain_compositions_checked"], 3)
        self.assertTrue(witness["all_direct_composition_checks_pass"])
        self.assertEqual(witness["direct_composition_checks"], 15)

    def test_principal_blocks_reproduce_T58(self) -> None:
        witness = self.packet["five_degree_exact_witness"]
        self.assertTrue(witness["all_principal_x0_blocks_match_T58"])
        self.assertTrue(all(row["principal_at_x0_matches_T58"] for row in witness["degree_rows"]))

    def test_lower_order_entries_are_derived_not_independent_rows(self) -> None:
        theorem = self.packet["coefficient_compiler_theorem"]
        contract = self.packet["q79_execution_contract_update"]
        self.assertEqual(theorem["independent_lower_order_matrix_rows_required_after_endpoint"], 0)
        self.assertEqual(contract["independent_coefficient_entry_source_rows_after_endpoint"], 0)
        self.assertEqual(contract["local_lower_order_coefficient_compiler"], "CLOSED_BY_CBF_T59")

    def test_neumann_inverse_certificate_is_strict(self) -> None:
        row = self.packet["projected_neumann_inverse_certificate"]
        self.assertEqual(Fraction(row["eta"]), Fraction(1, 3))
        self.assertEqual(Fraction(row["actual_error_operator_norm"]), Fraction(13, 8100))
        self.assertEqual(Fraction(row["certified_error_bound"]), Fraction(1, 162))
        self.assertLess(Fraction(row["actual_error_operator_norm"]), Fraction(row["certified_error_bound"]))

    def test_feshbach_tail_certificate_has_positive_margin(self) -> None:
        row = self.packet["feshbach_tail_certificate"]
        self.assertEqual(Fraction(row["tail_gap_gershgorin"]), Fraction(19, 4))
        self.assertEqual(Fraction(row["main_gap_gershgorin"]), Fraction(9, 5))
        self.assertGreater(Fraction(row["schur_lower_bound"]), 0)

    def test_kernel_projected_reduced_green_is_certified(self) -> None:
        checks = self.packet["check_summary"]["feshbach_subchecks"]
        self.assertTrue(checks["kernel_projector_exact"])
        self.assertTrue(checks["reduced_green_left_identity"])
        self.assertTrue(checks["reduced_green_right_identity"])
        self.assertTrue(checks["reduced_green_annihilates_kernel"])

    def test_q79_compiler_is_complete_but_values_are_open(self) -> None:
        contract = self.packet["q79_execution_contract_update"]
        self.assertEqual(contract["carrier_dimensions"], [1, 105, 309, 307, 102])
        self.assertEqual(contract["principal_preconditioner"], "CLOSED_BY_CBF_T58")
        self.assertEqual(contract["projected_global_inverse_acceptance_compiler"], "CLOSED_BY_CBF_T59")
        self.assertEqual(contract["Feshbach_tail_acceptance_compiler"], "CLOSED_BY_CBF_T59")
        self.assertEqual(contract["selected_endpoint_coefficient_values"], "OPEN")
        self.assertEqual(contract["selected_global_reduced_inverse"], "OPEN")

    def test_physical_blockers_remain_open(self) -> None:
        contract = self.packet["q79_execution_contract_update"]
        self.assertFalse(contract["B_GEO_01_closed"])
        self.assertFalse(contract["B_OP_01_closed"])

    def test_physical_counters_do_not_move(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertEqual(boundary["physical_gates"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_packets"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_rows"], {"accepted": 0, "total": 7})

    def test_witness_values_are_not_physical(self) -> None:
        self.assertFalse(self.packet["five_degree_exact_witness"]["fixtures_are_physical"])
        self.assertFalse(self.packet["projected_neumann_inverse_certificate"]["fixtures_are_physical"])
        self.assertFalse(self.packet["feshbach_tail_certificate"]["fixtures_are_physical"])

    def test_no_parameters_or_empirical_values_are_added(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["continuous_physical_parameters_added"], 0)
        self.assertEqual(ledger["discrete_selectors_added"], 0)
        self.assertEqual(ledger["observed_values_used"], 0)
        self.assertEqual(ledger["fitted_values_used"], 0)


if __name__ == "__main__":
    unittest.main()
