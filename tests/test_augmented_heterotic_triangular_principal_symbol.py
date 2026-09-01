from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "augmented_heterotic_triangular_principal_symbol.packet.json"


class AugmentedHeteroticTriangularPrincipalSymbolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_augmented_heterotic_triangular_principal_symbol.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))

    def test_builder_passes_all_checks(self) -> None:
        self.assertEqual(self.packet["check_summary"]["total"], 52)
        self.assertTrue(self.packet["check_summary"]["all_passed"])

    def test_independent_verifier_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_augmented_heterotic_triangular_principal_symbol.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn('"all_passed": true', result.stdout)
        self.assertIn('"total": 58', result.stdout)

    def test_symbol_complex_is_nilpotent_for_all_samples(self) -> None:
        witness = self.packet["exact_six_dimensional_witness"]
        self.assertEqual(witness["sample_count"], 21)
        self.assertTrue(witness["all_complex_symbols_nilpotent"])

    def test_mixed_second_order_blocks_cancel(self) -> None:
        witness = self.packet["exact_six_dimensional_witness"]
        self.assertTrue(witness["all_Hodge_off_diagonal_second_order_blocks_cancel"])

    def test_nonscalar_correction_is_rank_six_projector(self) -> None:
        witness = self.packet["exact_six_dimensional_witness"]
        self.assertTrue(witness["all_corrections_are_rank_six_orthogonal_projectors"])
        self.assertTrue(witness["scalar_full_symbol_negative_control_passes"])

    def test_every_symbol_has_exactly_two_levels(self) -> None:
        witness = self.packet["exact_six_dimensional_witness"]
        self.assertTrue(witness["all_symbols_have_exactly_two_levels"])
        self.assertEqual(witness["baseline_multiplicity"], 9)
        self.assertEqual(witness["elevated_multiplicity"], 6)

    def test_relative_lane_normalization_is_recovered(self) -> None:
        witness = self.packet["exact_six_dimensional_witness"]
        self.assertEqual(Fraction(witness["normalized_trace_factor"]), Fraction(11, 10))
        self.assertEqual(Fraction(witness["recovered_relative_lane_normalization"]), 1)

    def test_metric_action_scale_and_hodge_are_recovered(self) -> None:
        recovery = self.packet["same_source_recovery"]
        self.assertTrue(recovery["action_quadratic_reconstruction_exact"])
        self.assertTrue(recovery["action_scale_reconstruction_exact"])
        self.assertTrue(recovery["metric_reconstruction_exact"])
        self.assertTrue(recovery["inverse_metric_reconstruction_exact"])
        self.assertTrue(recovery["Hodge_reconstruction_matches_T55"])

    def test_q79_rank102_specialization_is_exact(self) -> None:
        q79 = self.packet["q79_rank102_specialization"]
        self.assertEqual(q79["degree_one_dimension"], 309)
        self.assertEqual(q79["baseline_multiplicity"], 303)
        self.assertEqual(q79["elevated_multiplicity"], 6)
        self.assertEqual(q79["normalized_trace_factor_formula"], "1+rho/206")
        self.assertEqual(Fraction(q79["rho_one_benchmark_trace_factor"]), Fraction(207, 206))

    def test_T56_is_restricted_not_retracted(self) -> None:
        theorem = self.packet["triangular_symbol_theorem"]
        self.assertFalse(theorem["full_augmented_symbol_is_scalar"])
        self.assertIn("diagonal", theorem["T56_scope_correction"])

    def test_duplicate_rho_and_metric_sources_are_removed(self) -> None:
        contract = self.packet["q79_source_contract_update"]
        self.assertEqual(contract["independent_scalar_full_symbol_obligation"], "REMOVED_AS_FALSE_REQUIREMENT")
        self.assertEqual(contract["independent_relative_lane_normalization_after_full_selected_symbol"], 0)
        self.assertEqual(contract["independent_metric_payload_after_full_selected_symbol_and_density"], 0)

    def test_parameter_ledger_adds_no_physical_knobs(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["continuous_physical_parameters_added"], 0)
        self.assertEqual(ledger["discrete_selectors_added"], 0)
        self.assertEqual(ledger["observed_values_used"], 0)
        self.assertEqual(ledger["fitted_values_used"], 0)
        self.assertTrue(ledger["rho_is_recovered_not_fitted_once_full_symbol_is_selected"])

    def test_physical_endpoint_and_blockers_remain_open(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertFalse(boundary["B_GEO_01_closed"])
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertFalse(boundary["B_OP_01_closed"])
        self.assertEqual(boundary["physical_gates"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_packets"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_rows"], {"accepted": 0, "total": 7})


if __name__ == "__main__":
    unittest.main()
