from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "same_source_principal_symbol_metric_hodge_naturality.packet.json"


def load_packet() -> dict:
    return json.loads(PACKET_PATH.read_text(encoding="utf-8"))


class SameSourcePrincipalSymbolMetricHodgeNaturalityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_same_source_principal_symbol_metric_hodge_naturality.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = load_packet()

    def test_builder_passes_all_checks(self) -> None:
        self.assertEqual(self.packet["check_summary"]["passed"], 35)
        self.assertTrue(self.packet["check_summary"]["all_passed"])

    def test_independent_verifier_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_same_source_principal_symbol_metric_hodge_naturality.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn('"passed": 41', result.stdout)

    def test_complete_polarization_sample_set_is_emitted(self) -> None:
        benchmark = self.packet["exact_non_diagonal_benchmark"]
        self.assertEqual(benchmark["symbol_sample_count"], 21)
        self.assertTrue(benchmark["all_symbol_samples_scalar"])

    def test_action_scale_and_metric_are_reconstructed_exactly(self) -> None:
        benchmark = self.packet["exact_non_diagonal_benchmark"]
        self.assertEqual(benchmark["recovered_action_scale"], "7")
        self.assertTrue(benchmark["A_reconstruction_exact"])
        self.assertTrue(benchmark["metric_reconstruction_exact"])
        self.assertTrue(benchmark["inverse_metric_reconstruction_exact"])

    def test_full_Hodge_response_matches_T52(self) -> None:
        benchmark = self.packet["exact_non_diagonal_benchmark"]
        self.assertTrue(benchmark["Hodge_reconstruction_matches_T52"])
        self.assertEqual(
            benchmark["Hodge_reconstruction_sha256"],
            benchmark["source_Hodge_sha256"],
        )

    def test_base_and_gauge_naturality_are_exact(self) -> None:
        naturality = self.packet["naturality_certificate"]
        self.assertEqual(naturality["coframe_change_determinant"], "1")
        self.assertTrue(naturality["full_Hodge_pullback_naturality"])
        self.assertTrue(naturality["gauge_and_base_naturality_exact"])

    def test_all_eight_shape_variations_pass_through_symbol_chain(self) -> None:
        response = self.packet["first_variation_certificate"]
        self.assertEqual(response["shape_direction_count"], 8)
        self.assertTrue(response["all_metric_directions_recovered"])
        self.assertTrue(response["all_Hodge_derivatives_match_T52"])
        self.assertEqual(response["composite_Hodge_response_rank"], 8)

    def test_density_is_a_necessary_scale_input(self) -> None:
        cutset = self.packet["necessity_cutsets"]["without_density"]
        self.assertTrue(cutset["same_action_quadratic"])
        self.assertNotEqual(
            cutset["first_candidate_density"], cutset["second_candidate_density"]
        )
        self.assertTrue(cutset["one_positive_scale_orbit_remains"])

    def test_trace_only_nonscalar_promotion_is_rejected(self) -> None:
        cutset = self.packet["necessity_cutsets"]["without_scalarity"]
        self.assertTrue(cutset["trace_matches_scalar_sample"])
        self.assertGreater(cutset["scalar_residual_rank"], 0)
        self.assertTrue(cutset["trace_only_metric_promotion_rejected"])

    def test_shape_degrees_remain_but_duplicate_payload_does_not(self) -> None:
        contract = self.packet["q79_source_contract_update"]
        self.assertEqual(contract["intrinsic_Hermitian_shape_dimension_after_T55"], 8)
        self.assertEqual(
            contract[
                "independent_metric_payload_after_accepted_same_source_symbol_and_density"
            ],
            0,
        )

    def test_selected_physical_source_is_not_promoted(self) -> None:
        contract = self.packet["q79_source_contract_update"]
        self.assertEqual(contract["selected_physical_GAS_instance"], "OPEN")
        self.assertEqual(contract["selected_q79_metric_values"], "OPEN")
        self.assertEqual(contract["selected_HYM_connection_and_Green"], "OPEN")

    def test_parameter_ledger_adds_nothing(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["continuous_parameters_added"], 0)
        self.assertEqual(ledger["discrete_selectors_added"], 0)
        self.assertEqual(ledger["observed_values_used"], 0)
        self.assertEqual(ledger["fitted_values_used"], 0)
        self.assertFalse(ledger["benchmark_action_scale_is_physical"])

    def test_physical_counters_do_not_move(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertEqual(boundary["physical_gates"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_packets"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_rows"], {"accepted": 0, "total": 7})

    def test_controlling_blockers_remain_open(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertFalse(boundary["B_GEO_01_closed"])
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertFalse(boundary["B_OP_01_closed"])


if __name__ == "__main__":
    unittest.main()

