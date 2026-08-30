from __future__ import annotations

import json
import unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json"


class RenormalizedBVAnchoredRepairSemiflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_builder_ledger_is_green(self) -> None:
        self.assertTrue(all(self.packet["checks"].values()))
        summary = self.packet["check_summary"]
        self.assertEqual(summary["passed"], summary["total"])
        self.assertEqual(summary["failed"], [])

    def test_full_bv_generator_has_all_four_typed_terms(self) -> None:
        generator = self.packet["quantum_bv_generator"]
        for key in (
            "action_term_included",
            "measure_term_included",
            "determinant_term_included",
            "cycle_boundary_term_included",
        ):
            self.assertTrue(generator[key])
        self.assertTrue(generator["terms_must_cancel_only_in_total"])
        self.assertFalse(generator["individual_termwise_vanishing_required"])

    def test_global_identity_radial_flow_is_excluded_in_bounded_scope(self) -> None:
        no_go = self.packet["global_intertwining_no_go"]
        self.assertTrue(no_go["q4_star_positive"])
        self.assertTrue(no_go["fifth_derivative_at_H_is_nonzero"])
        self.assertEqual(no_go["allowed_counterterm_fifth_derivative"], "0")
        self.assertFalse(no_go["global_identity_radial_repair_intertwining_possible"])
        self.assertFalse(no_go["no_go_is_universal_beyond_declared_scope"])

    def test_unique_anchor_retraction_matches_three_jets(self) -> None:
        anchor = self.packet["pointed_anchor_retraction"]
        witness = anchor["witness"]
        self.assertEqual(anchor["determinant"], "det(j_H^2|C_even)=16 H^3")
        self.assertEqual(Fraction(witness["matching_matrix_determinant_at_witness"]), 54)
        self.assertEqual(witness["total_remainder_jet_0_1_2"], ["0", "0", "0"])
        self.assertTrue(witness["counterterm_is_linear_over_four_BV_terms"])
        self.assertTrue(witness["retraction_is_linear_over_four_BV_terms"])
        self.assertTrue(witness["retraction_is_idempotent"])

    def test_t35_pointed_jets_close_but_nonlinear_terms_survive(self) -> None:
        execution = self.packet["T35_pointed_execution"]
        jets = execution["action_jets_at_x_equal_one"]
        self.assertEqual(
            [jets[key] for key in ("value", "first", "second", "third", "fourth", "fifth")],
            [0, 0, 0, -16, -64, -48],
        )
        self.assertTrue(execution["pointed_fixed_point_intertwining"])
        self.assertTrue(execution["pointed_tangent_intertwining_given_common_metric_at_H"])
        self.assertFalse(execution["global_repair_vector_fields_equal"])
        self.assertTrue(execution["nonlinear_quantum_corrections_retained"])

    def test_anchored_formal_flow_preserves_value_tadpole_and_hessian(self) -> None:
        flow = self.packet["anchored_formal_bv_flow"]
        self.assertEqual(flow["finite_normalization_conditions"], 3)
        self.assertEqual(flow["new_free_counterterm_coefficients"], 0)
        self.assertIn("Gamma_s^H(H)=0", flow["QJ1_formal_consequence"])
        self.assertIn("partial_h^2 Gamma_s^H(H)", flow["QJ2_formal_action_jet_consequence"])
        self.assertEqual(flow["QJ0_formal_action_jet_consequence"], "Gamma_s^H(H)=P_*(H)")

    def test_qme_compatibility_does_not_select_the_anchor(self) -> None:
        compatibility = self.packet["qme_and_ward_compatibility"]
        self.assertEqual(compatibility["local_gauge_anomaly_class"], [0, 0, 0, 0, 0])
        self.assertTrue(compatibility["formal_QME_compatible_scheme_exists"])
        self.assertFalse(compatibility["QME_selects_anchor_coefficients"])
        self.assertFalse(compatibility["Ward_identity_selects_anchor_coefficients"])

    def test_qj_tiers_are_not_conflated(self) -> None:
        qj = self.packet["QJ_classification"]
        self.assertEqual(qj["QJ1_local_formal_anchor_scheme"], "closed_constructively")
        self.assertEqual(qj["QJ1_selected_physical_q79_law"], "open")
        self.assertEqual(qj["QJ2_local_formal_action_Hessian"], "closed_constructively")
        self.assertEqual(qj["QJ2_physical_normalized_Hessian"], "open_tangent_metric_or_wavefunction")
        self.assertEqual(qj["QJ0_gravitational_absolute_vacuum"], "open")

    def test_no_new_physical_parameter_fit_or_observed_input(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_physical_continuous_parameters"], 0)
        self.assertEqual(ledger["new_physical_discrete_selectors"], 0)
        self.assertEqual(ledger["new_fits"], 0)
        self.assertEqual(ledger["new_observed_inputs"], 0)
        self.assertEqual(ledger["finite_anchor_normalization_conditions"], 3)
        self.assertFalse(ledger["anchor_conditions_are_a_physical_prediction"])

    def test_physical_acceptance_remains_open(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertFalse(boundary["physical_QJ1_selected"])
        self.assertFalse(boundary["physical_QJ2_selected"])
        self.assertFalse(boundary["gravitational_QJ0_selected"])
        self.assertFalse(boundary["physical_interacting_q79_BV_endpoint_executed"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
