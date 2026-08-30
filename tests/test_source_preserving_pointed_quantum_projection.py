from __future__ import annotations

import json
import unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "source_preserving_pointed_quantum_projection.packet.json"


class SourcePreservingPointedQuantumProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_exact_counterterm_matrix_is_invertible(self) -> None:
        orbit = self.packet["finite_counterterm_orbit"]
        self.assertEqual(Fraction(orbit["rational_witness_H"]), Fraction(3, 2))
        self.assertEqual(Fraction(orbit["rational_witness_determinant"]), 54)
        self.assertEqual(orbit["symbolic_determinant"], "16 H^3")

    def test_qj1_leaves_one_nonconstant_direction(self) -> None:
        orbit = self.packet["finite_counterterm_orbit"]
        self.assertEqual(orbit["QJ1_map_rank"], 1)
        self.assertEqual(orbit["QJ1_kernel_dimension_mod_constants"], 1)
        self.assertEqual(orbit["QJ1_kernel_vector_a_b"], ["-9/2", "1"])
        self.assertEqual(orbit["QJ1_kernel_first_derivative"], "0")
        self.assertEqual(orbit["QJ1_kernel_second_derivative"], "18")

    def test_qj1_and_qj2_kill_nonconstant_scheme_freedom(self) -> None:
        orbit = self.packet["finite_counterterm_orbit"]
        self.assertEqual(orbit["QJ1_plus_QJ2_rank"], 2)
        self.assertEqual(orbit["QJ1_plus_QJ2_kernel_mod_constants"], 0)
        self.assertTrue(orbit["constant_survives_QJ1_QJ2"])

    def test_quantum_identities_do_not_select_the_scheme(self) -> None:
        result = self.packet["ward_qme_ppa_nonselection"]
        self.assertTrue(result["formal_QME_scheme_exists"])
        self.assertTrue(result["SP_freedom_remains"])
        self.assertFalse(result["QME_selects_finite_coefficients"])
        self.assertFalse(result["gauge_Ward_selects_finite_coefficients"])
        self.assertFalse(result["Action_Ward_selects_finite_coefficients"])
        self.assertFalse(result["split_Ward_selects_finite_coefficients"])
        self.assertFalse(result["perturbative_agreement_selects_total_action"])

    def test_classical_on_shell_clause_does_not_remove_quantum_tadpole(self) -> None:
        result = self.packet["ward_qme_ppa_nonselection"]
        self.assertTrue(result["classical_on_shell_background_removes_linear_tree_term"])
        self.assertFalse(result["classical_on_shell_clause_selects_quantum_tadpole_scheme"])
        self.assertTrue(result["T35_bare_tadpole_nonzero"])

    def test_provider_contract_contains_required_source_data(self) -> None:
        contract = self.packet["source_preserving_projection_contract"]
        self.assertTrue(contract["provider_schema_requires_fixed_point_hessian_identity"])
        self.assertTrue(contract["provider_schema_requires_action_bv_pushforward"])
        self.assertTrue(contract["provider_schema_requires_normalization_source"])
        self.assertTrue(contract["provider_schema_requires_one_root_hash"])
        self.assertEqual(set(contract["clauses"]), {"SP0", "SP1", "SP2", "SP3", "SP4", "SP5"})

    def test_one_morphism_implies_qj1_and_action_qj2(self) -> None:
        theorem = self.packet["selection_theorem"]
        self.assertTrue(theorem["QJ1_follows_from_one_morphism"])
        self.assertTrue(theorem["action_jet_QJ2_follows_from_same_morphism"])
        self.assertFalse(theorem["QJ1_and_action_QJ2_are_independent_numeric_knobs"])
        self.assertTrue(theorem["unique_representative_is_T39_anchor"])

    def test_t35_qj1_direction_is_hessian_visible(self) -> None:
        execution = self.packet["T35_execution"]
        direction = execution["QJ1_orbit_direction"]
        self.assertTrue(execution["QJ1_orbit_tadpole_is_zero"])
        self.assertTrue(execution["QJ1_orbit_hessian_is_nonzero"])
        self.assertEqual(Decimal(direction["delta_lambda_over_kappa_per_t"]), 1)
        self.assertGreater(Decimal(direction["hessian_shift_over_kappa_Lambda2_per_t"]), 0)

    def test_radial_marginal_does_not_require_unique_full_state(self) -> None:
        state = self.packet["radial_state_route"]
        self.assertTrue(state["unique_upper_radial_marginal"])
        self.assertFalse(state["full_gauge_matter_state_uniqueness_required_for_radial_QJ1"])
        self.assertFalse(state["selected_physical_state_pushforward_present"])

    def test_physical_boundary_is_not_promoted(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertTrue(boundary["provider_contract_level_selector_proved"])
        self.assertFalse(boundary["selected_physical_quantum_projection_present"])
        self.assertFalse(boundary["physical_QJ1_selected"])
        self.assertFalse(boundary["physical_QJ2_selected"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)

    def test_parameter_ledger_has_one_structural_exit_and_no_new_knob(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_physical_continuous_parameters"], 0)
        self.assertEqual(ledger["new_physical_discrete_selectors"], 0)
        self.assertEqual(ledger["new_observed_inputs"], 0)
        self.assertEqual(ledger["new_structural_existence_certificates_required"], 1)


if __name__ == "__main__":
    unittest.main()
