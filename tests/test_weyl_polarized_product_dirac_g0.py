from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "weyl_polarized_product_dirac_g0.packet.json"


class WeylPolarizedProductDiracG0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_weyl_polarized_product_dirac_g0.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_builder_packet_passes(self) -> None:
        summary = self.packet["check_summary"]
        self.assertEqual(summary["failed"], [])
        self.assertEqual(summary["passed"], summary["total"])

    def test_carrier_ledger_does_not_double_KO6(self) -> None:
        carrier = self.packet["carrier_ledger"]
        self.assertEqual(carrier["three_family_left_Weyl_internal_dimension"], 48)
        self.assertEqual(carrier["KO6_real_completion_dimension"], 96)
        self.assertEqual(carrier["continuum_left_Weyl_component_dimension"], 96)
        self.assertTrue(carrier["KO6_completion_is_not_an_independent_field_copy"])

    def test_response_multiplicities_exhaust_Weyl_carrier(self) -> None:
        carrier = self.packet["carrier_ledger"]
        self.assertEqual(carrier["branch_multiplicities"], {"-4": 16, "-2": 16, "2": 16})
        self.assertEqual(carrier["branch_multiplicity_sum"], 48)

    def test_Weyl_exponent_selects_half_candidate(self) -> None:
        exponent = self.packet["determinant_exponent"]
        self.assertEqual(exponent["selected_kappa_F"], "1/(2 pi^2)")
        self.assertEqual(Fraction(exponent["selected_kappa_F_times_pi_squared"]), Fraction(1, 2))
        self.assertEqual(exponent["rejected_doubled_candidate"], "1/pi^2")

    def test_q4_is_exact(self) -> None:
        q4 = self.packet["exact_finite_trace"]["q4_star"]["exact_coefficients"]
        self.assertEqual(q4, {"rational": "356/27", "sqrt13": "25/27"})

    def test_rho_is_derived_not_supplied(self) -> None:
        renorm = self.packet["pointed_renormalization"]
        self.assertEqual(
            [Fraction(value) for value in renorm["interpolation_coefficients_c0_c2_c4"]],
            [Fraction(-1, 2), Fraction(2), Fraction(-3, 2)],
        )
        self.assertTrue(renorm["rho_is_output_not_input"])
        self.assertTrue(self.packet["source_provenance"]["comparison_sources_excluded_from_root"])

    def test_complete_pointed_jet_is_emitted(self) -> None:
        jets = [
            Fraction(value)
            for value in self.packet["pointed_renormalization"]["remainder_jets_at_x1_through_order5"]
        ]
        self.assertEqual(jets, [0, 0, 0, -16, -64, -48])

    def test_higher_vertex_values_are_fixed(self) -> None:
        emitted = self.packet["emitted_action"]
        self.assertEqual(emitted["third_vertex_shift"], "-8 q4_* H/pi^2")
        self.assertEqual(emitted["fourth_vertex_shift"], "-32 q4_*/pi^2")
        self.assertEqual(emitted["fifth_vertex_shift"], "-24 q4_*/(pi^2 H)")

    def test_transitive_source_graph_passes(self) -> None:
        graph = self.packet["same_source_graph"]
        self.assertTrue(graph["all_edges_verified"])
        self.assertTrue(all(graph["verified_edges"].values()))
        self.assertTrue(graph["direct_operator_and_one_loop_action_share_root"])

    def test_T42_is_compatible_but_not_identified(self) -> None:
        comparison = self.packet["T42_comparison"]
        self.assertTrue(comparison["normalized_scalar_remainder_matches"])
        self.assertTrue(comparison["T42_is_target_informed"])
        self.assertFalse(comparison["operators_identified"])
        self.assertFalse(comparison["q79_rank_four_counts_physical_particles"])

    def test_direct_G0_advances_without_moving_physical_counters(self) -> None:
        gates = self.packet["gate_ledger"]
        self.assertTrue(gates["G0_direct_local_one_loop"]["closed"])
        self.assertFalse(gates["G0_global_physical"]["closed"])
        self.assertFalse(gates["G0_q79_HYM"]["closed"])
        self.assertEqual((gates["physical_gluing_gates_closed"], gates["physical_gluing_gates_total"]), (0, 3))
        self.assertEqual((gates["physical_rows_accepted"], gates["physical_rows_total"]), (0, 7))

    def test_no_new_fit_or_continuous_parameter(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_observed_inputs"], 0)
        self.assertEqual(ledger["new_fitted_coefficients"], 0)
        self.assertEqual(ledger["new_continuous_physical_parameters"], 0)
        self.assertEqual(
            (
                ledger["local_determinant_normalization_candidates_before"],
                ledger["local_determinant_normalization_candidates_after"],
            ),
            (2, 1),
        )

    def test_global_and_HYM_boundaries_remain_open(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertFalse(boundary["global_Wick_or_direct_Lorentzian_determinant_closed"])
        self.assertFalse(boundary["q79_HYM_normal_operator_closed"])
        self.assertFalse(boundary["direct_and_q79_HYM_routes_identified"])
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertFalse(boundary["B_QFT_02_closed"])

    def test_independent_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_weyl_polarized_product_dirac_g0.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("independent checks:", result.stdout)


if __name__ == "__main__":
    unittest.main()
