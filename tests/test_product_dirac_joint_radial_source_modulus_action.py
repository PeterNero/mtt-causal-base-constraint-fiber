from __future__ import annotations

import json
import unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "product_dirac_joint_radial_source_modulus_action.packet.json"


class ProductDiracJointRadialSourceModulusActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_action_scope_is_explicitly_conditional(self) -> None:
        scope = self.packet["conditional_action_scope"]
        self.assertEqual(scope["product_Dirac_scalar"], "Phi(x)=h(x)D_phys(t(x))")
        self.assertTrue(scope["A51_one_Higgs_module_selected"])
        self.assertFalse(scope["t_is_an_A51_inner_fluctuation"])
        self.assertFalse(scope["t_field_promotion_selected_by_MTT"])
        self.assertFalse(scope["global_Wick_or_Lorentzian_action_selected"])

    def test_exact_trace_polynomials_are_reconstructed(self) -> None:
        traces = self.packet["exact_trace_data"]
        self.assertEqual(traces["q2_coefficients_ascending"], ["3", "-4", "6"])
        self.assertEqual(
            traces["q4_coefficients_ascending"],
            ["3", "-8", "36", "-32", "18"],
        )
        self.assertEqual(traces["Tr_D1_squared"], "192")
        self.assertTrue(traces["matrix_reconstruction_exact"])

    def test_source_modulus_has_a_conditional_positive_kinetic_metric(self) -> None:
        geometry = self.packet["field_space_geometry"]
        self.assertEqual(geometry["determinant"], "14h^2")
        self.assertEqual(geometry["positive_definite_domain"], "h>0")
        self.assertTrue(geometry["conditional_t_kinetic_term_closed"])
        self.assertFalse(geometry["selected_t_dynamicality_closed"])

    def test_joint_tree_vacuum_has_no_nonzero_family_hierarchy(self) -> None:
        vacuum = self.packet["vacuum_selection"]
        self.assertEqual(vacuum["inner_quadratic_discriminant"], -432)
        self.assertEqual(vacuum["equality_condition"], "t=0 only")
        self.assertEqual(vacuum["unique_broken_stationary_coordinate_in_chamber"], "t0=0")
        self.assertEqual(vacuum["unique_radial_vacuum_for_h>=0"], "h0^2=2c")
        self.assertFalse(vacuum["nonzero_family_hierarchy_at_tree_level"])
        self.assertFalse(vacuum["fixed_h_nonzero_candidates_survive_joint_h_equation"])

    def test_scalar_curvature_spectrum_is_exactly_degenerate(self) -> None:
        spectrum = self.packet["scalar_spectrum"]
        self.assertEqual(spectrum["exact_relation"], "Hess(P)|0=8h0^2 g|0")
        self.assertEqual(spectrum["generalized_mass_squared_spectrum"], {"4h0^2": 2})
        self.assertEqual(spectrum["dimensionless_mass_ratio"], "m/h0=2")
        self.assertIn("not pole masses", spectrum["interpretation"])

    def test_repair_action_is_the_rho_one_fixed_radial_slice(self) -> None:
        bridge = self.packet["fixed_radial_bridge"]
        self.assertEqual(bridge["rho_one_identity"], "U_1(t)-U_1(0)=6S_rep(t)")
        self.assertEqual(bridge["S_rep"], "4t^2-(16/3)t^3+3t^4")
        self.assertEqual(bridge["source"], "CBF.T26")

    def test_A53_premise_emits_certified_conditional_ratios(self) -> None:
        compatibility = self.packet["A53_T23_compatibility"]
        ratios = compatibility["A53_conditional_ratios"]
        h_lower = Decimal(ratios["h0_over_Lambda_interval"]["lower_decimal"])
        h_upper = Decimal(ratios["h0_over_Lambda_interval"]["upper_decimal"])
        m_lower = Decimal(ratios["mass_over_Lambda_interval"]["lower_decimal"])
        m_upper = Decimal(ratios["mass_over_Lambda_interval"]["upper_decimal"])
        self.assertLess(h_lower, h_upper)
        self.assertLess(m_lower, m_upper)
        self.assertLess(h_lower, Decimal("2.2167930327239011163923090045105"))
        self.assertGreater(h_upper, Decimal("2.2167930327239011163923090045105"))
        h_lower_exact = Fraction(ratios["h0_over_Lambda_interval"]["lower_exact"])
        h_upper_exact = Fraction(ratios["h0_over_Lambda_interval"]["upper_exact"])
        m_lower_exact = Fraction(ratios["mass_over_Lambda_interval"]["lower_exact"])
        m_upper_exact = Fraction(ratios["mass_over_Lambda_interval"]["upper_exact"])
        self.assertEqual(m_lower_exact, 2 * h_lower_exact)
        self.assertEqual(m_upper_exact, 2 * h_upper_exact)

    def test_A53_and_T23_stationary_normalizations_are_incompatible(self) -> None:
        compatibility = self.packet["A53_T23_compatibility"]
        self.assertFalse(compatibility["A53_one_atom_premise_selected_by_MTT"])
        self.assertEqual(
            compatibility["stationarity_with_h_equals_Lambda_requires"],
            "f2/f0=1/2, equivalently tau_int=2",
        )
        self.assertFalse(compatibility["A53_and_T23_stationary_combination_compatible"])
        self.assertEqual(len(compatibility["exact_exit_options"]), 3)

    def test_no_new_fit_or_accepted_parameter_is_hidden(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_observed_construction_inputs"], 0)
        self.assertEqual(ledger["new_fitted_coefficients"], 0)
        self.assertEqual(ledger["new_accepted_physical_parameters"], 0)
        self.assertEqual(ledger["conditional_structural_extensions"], 1)
        self.assertEqual(ledger["conditional_A53_premises"], 1)
        self.assertFalse(ledger["absolute_dimensionful_scale_selected"])

    def test_physical_acceptance_boundary_does_not_move(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertTrue(boundary["conditional_joint_heat_kernel_action_closed"])
        self.assertTrue(boundary["standard_tree_action_nonzero_hierarchy_no_go_closed"])
        self.assertFalse(boundary["selected_source_modulus_field_closed"])
        self.assertFalse(boundary["selected_spectral_moments_closed"])
        self.assertFalse(boundary["selected_absolute_scale_closed"])
        self.assertFalse(boundary["measured_mass_prediction_closed"])
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertFalse(boundary["B_QFT_02_closed"])
        self.assertFalse(boundary["B_SM_02_closed"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)

    def test_builder_check_ledger_is_green(self) -> None:
        summary = self.packet["check_summary"]
        self.assertEqual(summary["passed"], summary["total"])
        self.assertEqual(summary["failed"], [])
        self.assertTrue(all(self.packet["checks"].values()))


if __name__ == "__main__":
    unittest.main()
