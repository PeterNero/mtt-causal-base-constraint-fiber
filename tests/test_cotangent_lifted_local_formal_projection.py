from __future__ import annotations

import json
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "cotangent_lifted_local_formal_projection.packet.json"


class CotangentLiftedLocalFormalProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_all_four_components_are_assembled(self) -> None:
        self.assertEqual(self.packet["component_packets_assembled"], 4)
        self.assertEqual(self.packet["component_packets_total"], 4)
        self.assertTrue(self.packet["component_product"]["all_component_certificates_pass"])

    def test_component_product_is_not_retyped_as_physical_projection(self) -> None:
        product = self.packet["component_product"]
        self.assertFalse(product["component_domains_identified_by_one_map"])
        self.assertFalse(product["component_product_is_physical_fiber_product"])
        self.assertFalse(product["observable_evaluation_is_covariant_BV_field_projection"])

    def test_action_jet_retraction_is_exact(self) -> None:
        jet = self.packet["exact_finite_witness"]["action_jet_retraction"]
        self.assertEqual(Fraction(jet["anchor_H"]), Fraction(3, 2))
        self.assertEqual(Fraction(jet["restricted_even_determinant"]), 54)
        self.assertTrue(jet["C_H_idempotent"])
        self.assertTrue(jet["R_H_idempotent"])
        self.assertTrue(jet["jet_C_H_equals_jet"])
        self.assertTrue(jet["jet_R_H_zero"])

    def test_cotangent_lift_preserves_retained_pairing(self) -> None:
        cotangent = self.packet["exact_finite_witness"]["cotangent_contraction"]
        self.assertTrue(cotangent["primal_projection_after_inclusion"])
        self.assertTrue(cotangent["primal_contraction_identity"])
        self.assertTrue(cotangent["cotangent_projection_after_inclusion"])
        self.assertTrue(cotangent["cotangent_contraction_identity"])
        self.assertTrue(cotangent["cotangent_inclusion_is_symplectic"])

    def test_plain_projection_kills_discarded_pairing(self) -> None:
        cotangent = self.packet["exact_finite_witness"]["cotangent_contraction"]
        self.assertEqual(Fraction(cotangent["discarded_pairing_before_projection"]), 1)
        self.assertEqual(Fraction(cotangent["discarded_pairing_after_projection"]), 0)

    def test_free_shell_cycle_is_lagrangian_and_nondegenerate(self) -> None:
        shell = self.packet["exact_finite_witness"]["free_shell_BV"]
        self.assertTrue(shell["Q_squared_zero"])
        self.assertTrue(shell["Q_preserves_odd_pairing"])
        self.assertTrue(shell["Hodge_contraction_identity"])
        self.assertTrue(shell["L_shell_is_lagrangian"])
        self.assertTrue(shell["restricted_quadratic_is_nondegenerate"])
        self.assertEqual(Fraction(shell["restricted_quadratic_determinant"]), -1)

    def test_radial_marginal_does_not_select_matter_state(self) -> None:
        state = self.packet["exact_finite_witness"]["radial_and_matter_states"]
        self.assertEqual(Fraction(state["radial_variance"]), 0)
        self.assertTrue(state["both_states_positive"])
        self.assertTrue(state["both_states_normalized"])
        self.assertEqual(state["both_radial_marginals"], "delta_H")
        self.assertNotEqual(state["omega_0_sigma_z"], state["omega_1_sigma_z"])
        self.assertFalse(state["full_state_selected_by_radial_marginal"])

    def test_same_root_gate_is_independent(self) -> None:
        gate = self.packet["independent_gluing_gates"]["G0_same_root"]
        self.assertTrue(gate["component_matrices_identical"])
        self.assertTrue(gate["root_hashes_distinct"])
        self.assertFalse(gate["same_root_follows_from_numeric_component_equality"])

    def test_physical_metric_gate_is_independent(self) -> None:
        gate = self.packet["independent_gluing_gates"]["G1_physical_tangent_pairing"]
        self.assertEqual(Fraction(gate["isometry_defect"]), 3)
        self.assertTrue(gate["internal_A35_unit_line_unchanged"])
        self.assertFalse(gate["physical_isometry_follows_from_internal_unit_line"])

    def test_interacting_state_gate_is_independent(self) -> None:
        gate = self.packet["independent_gluing_gates"]["G2_selected_interacting_state_BV"]
        self.assertTrue(gate["two_positive_normalized_matter_states"])
        self.assertTrue(gate["free_shell_pushforward_shared"])
        self.assertFalse(gate["preferred_interacting_state_follows"])

    def test_promotion_requires_exactly_three_gates(self) -> None:
        criterion = self.packet["promotion_criterion"]
        self.assertTrue(criterion["necessary"])
        self.assertTrue(criterion["sufficient"])
        self.assertEqual(criterion["G0_implies_SP"], ["SP0", "SP1", "SP2", "SP3"])
        self.assertEqual(criterion["G1_implies_SP"], ["SP4"])
        self.assertEqual(criterion["G2_implies_SP"], ["SP5"])
        self.assertFalse(criterion["existence_proved"])

    def test_physical_boundary_and_parameter_ledger_are_unchanged(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertFalse(boundary["selected_physical_projection_constructed"])
        self.assertFalse(boundary["physical_QJ1_selected"])
        self.assertFalse(boundary["physical_QJ2_selected"])
        self.assertEqual(self.packet["physical_gluing_gates_closed"], 0)
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_physical_continuous_parameters"], 0)
        self.assertEqual(ledger["new_physical_discrete_selectors"], 0)
        self.assertEqual(ledger["new_fits"], 0)
        self.assertEqual(ledger["new_observed_inputs"], 0)


if __name__ == "__main__":
    unittest.main()
