from __future__ import annotations

import json
import unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "radial_closure_attractor_state_marginal.packet.json"


class RadialClosureAttractorStateMarginalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_builder_ledger_is_green(self) -> None:
        self.assertTrue(all(self.packet["checks"].values()))
        summary = self.packet["check_summary"]
        self.assertEqual(summary["passed"], summary["total"])
        self.assertEqual(summary["failed"], [])

    def test_square_completion_uses_exact_T34_source(self) -> None:
        square = self.packet["exact_radial_square_completion"]
        self.assertTrue(square["ratio_identity_exact"])
        self.assertEqual(
            square["exact_completion"],
            "P_*(h)-P_*(H)=q4_* (h^2-H^2)^2",
        )
        self.assertGreater(Decimal(square["q4_star"]["decimal"]), 0)
        self.assertGreater(Decimal(square["H_over_Lambda_decimal"]), 0)
        self.assertFalse(square["new_coefficient_introduced"])

    def test_closed_radial_flow_converges_from_both_sides(self) -> None:
        flow = self.packet["nonlinear_repair_flow"]
        below = flow["flow_samples"][0]
        above = flow["flow_samples"][-1]
        self.assertLess(Decimal(below["h_at_s_over_H"]), 1)
        self.assertGreater(Decimal(above["h_at_s_over_H"]), 1)
        self.assertTrue(below["error_contracts"])
        self.assertTrue(above["error_contracts"])
        self.assertTrue(flow["global_positive_basin_converges_to_H"])

    def test_flow_has_correct_fixed_point_stability_and_semigroup(self) -> None:
        flow = self.packet["nonlinear_repair_flow"]
        self.assertGreater(Decimal(flow["zero_branch_linearization"]), 0)
        self.assertLess(Decimal(flow["positive_branch_linearization"]), 0)
        self.assertTrue(flow["semigroup_composition_verified"])
        self.assertFalse(flow["repair_parameter_is_physical_time"])

    def test_zero_defect_probability_is_uniquely_delta_H(self) -> None:
        state = self.packet["invariant_radial_state"]
        defects = [Fraction(value) for value in state["dimensionless_defect_values"]]
        self.assertEqual(defects, [Fraction(9, 16), Fraction(0), Fraction(9)])
        self.assertEqual(
            state["unique_zero_defect_probability_weights"], ["0", "1", "0"]
        )
        self.assertIn("delta_H", state["invariant_state_theorem"])

    def test_gns_support_forces_radial_expectation_only(self) -> None:
        state = self.packet["invariant_radial_state"]
        self.assertEqual(state["forced_radial_expectation"], "omega(h)=H")
        self.assertEqual(state["forced_radial_variance"], "omega((h-H)^2)=0")
        self.assertTrue(state["radial_marginal_is_unique_without_selecting_matter_state"])

    def test_formal_q79_state_pullback_is_positive_but_not_unique(self) -> None:
        extension = self.packet["formal_q79_state_extension"]
        self.assertTrue(extension["q79_local_formal_state_spaces_nonempty"])
        self.assertEqual(
            Fraction(extension["finite_test_square_expectation"]), Fraction(233, 108)
        )
        self.assertTrue(extension["finite_test_square_is_positive"])
        self.assertTrue(extension["formal_local_radial_anchored_state_exists"])
        self.assertFalse(extension["full_interacting_state_is_unique"])
        self.assertFalse(extension["single_global_cosmological_state_constructed"])

    def test_semiflow_projection_naturality_would_close_QJ1(self) -> None:
        naturality = self.packet["repair_semiflow_projection_naturality"]
        self.assertTrue(naturality["finite_witness_intertwines"])
        self.assertEqual(Decimal(naturality["maximum_projection_commutator_residual"]), 0)
        self.assertTrue(naturality["QJ1_follows_from_physical_semiflow_intertwiner"])
        self.assertTrue(naturality["generic_action_pushforward_is_not_sufficient"])
        self.assertFalse(naturality["physical_q79_BV_semiflow_intertwiner_present"])

    def test_T35_bare_loop_is_the_nonzero_intertwining_defect(self) -> None:
        defect = self.packet["T35_quantum_intertwining_defect"]
        self.assertLess(
            Decimal(defect["lower_bare_tadpole_over_kappa_Lambda3"]),
            Decimal("-100"),
        )
        self.assertFalse(defect["bare_truncated_projection_intertwines_T34_flow"])
        self.assertTrue(defect["both_declared_determinant_branches_fail_bare_QJ1"])
        self.assertFalse(defect["QJ1_counterterm_line_selected_by_current_upper_action"])

    def test_no_fit_and_physical_boundary_are_preserved(self) -> None:
        ledger = self.packet["parameter_ledger"]
        boundary = self.packet["physical_boundary"]
        self.assertEqual(ledger["new_continuous_parameters"], 0)
        self.assertEqual(ledger["new_discrete_choices"], 0)
        self.assertEqual(ledger["observed_values_used"], [])
        self.assertEqual(ledger["fitted_values_used"], [])
        self.assertTrue(boundary["T34_unique_invariant_radial_state_closed"])
        self.assertFalse(boundary["physical_QJ1_selected"])
        self.assertFalse(boundary["physical_QJ2_selected"])
        self.assertFalse(boundary["physical_QJ0_selected"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
