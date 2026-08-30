from __future__ import annotations

import json
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "same_root_state_repair_heat_profile_radial_values.packet.json"


class SameRootStateRepairHeatProfileRadialValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_finite_selector_and_heat_profile_share_the_totalization_root(self) -> None:
        diagram = self.packet["same_root_commuting_diagram"]
        self.assertEqual(diagram["root"], "R_tot=(q_Y,q_F(t),Gamma_Y,h,totalize)")
        self.assertIn("q_F(t)", diagram["finite_factor_readout"])
        self.assertIn("B_tot(t,h)", diagram["total_charge_readout"])
        self.assertTrue(diagram["commutes_by_factor_functoriality"])
        self.assertFalse(diagram["comparison_matrix_inserted"])
        self.assertEqual(diagram["lower_evaluation"], "freeze t=t_* before varying h")

    def test_state_space_functional_generates_the_heat_semigroup(self) -> None:
        repair = self.packet["state_space_quadratic_repair"]
        self.assertEqual(repair["positive_generator"], "K=B_tot^2/Lambda^2>=0")
        self.assertEqual(repair["gradient"], "grad J_B=K Psi")
        self.assertEqual(repair["unique_solution"], "T_s=exp(-sK)")
        self.assertTrue(repair["contraction_for_nonnegative_s"])
        self.assertFalse(repair["new_clock_normalization_added"])

    def test_scalar_profile_has_no_shape_parameter(self) -> None:
        profile = self.packet["heat_profile_selection"]
        self.assertEqual(profile["profile"], "chi_s(x)=exp(-s x)")
        self.assertEqual(profile["shape_parameters_remaining"], 0)
        self.assertFalse(profile["overall_positive_trace_amplitude_relevant_to_ratio"])
        self.assertFalse(profile["full_nonlinear_Lorentzian_BV_action_claimed"])

    def test_A84_supplies_the_action_shadow_bridge(self) -> None:
        bridge = self.packet["action_shadow_bridge"]
        self.assertEqual(bridge["authority"], "A84")
        self.assertEqual(bridge["uninserted_scalar_trace"], "Tr exp(-sK)=Tr chi_s(K)")
        self.assertFalse(bridge["semigroup_alone_would_select_action_profile"])
        self.assertTrue(bridge["bridge_closed_at_regime_local_action_tier"])
        self.assertFalse(bridge["full_matching_completeness_closed"])
        self.assertFalse(bridge["full_nonlinear_physical_action_closed"])

    def test_positive_laplace_measure_is_unique_not_minimal_by_axiom(self) -> None:
        measure = self.packet["positive_laplace_measure"]
        self.assertEqual(measure["unique_measure"], "mu=A delta_s")
        self.assertEqual(measure["tilted_mean"], "E[u]=s")
        self.assertEqual(measure["tilted_variance"], "Var(u)=0")
        self.assertFalse(measure["minimal_support_axiom_used"])
        self.assertTrue(measure["A53_one_atom_measure_promoted_at_declared_tier"])

    def test_moment_ratios_are_selected_exactly(self) -> None:
        moments = self.packet["spectral_moments"]
        self.assertEqual(moments["f2_over_f0"], "1/s")
        self.assertEqual(moments["f4_over_f0"], "1/s^2")
        self.assertEqual(moments["rank_one_Hankel_identity"], "f0 f4-f2^2=0")
        self.assertEqual(moments["at_tau_f2_over_f0"], "15/log(448)")
        self.assertEqual(moments["at_tau_f4_over_f0"], "225/log(448)^2")

    def test_internal_checkpoint_does_not_identify_phase_with_time(self) -> None:
        checkpoint = self.packet["selected_internal_checkpoint"]
        self.assertEqual(checkpoint["gap"], 15)
        self.assertEqual(checkpoint["branch_order"], 448)
        self.assertEqual(checkpoint["identity"], "exp(-15 tau_int)=1/448")
        self.assertFalse(checkpoint["additive_physical_clock_lift_unconditional"])
        self.assertFalse(checkpoint["compact_phase_identified_with_Lorentzian_time"])

    def test_promoted_cutoff_unit_values_are_nonzero_and_ordered(self) -> None:
        promoted = self.packet["promoted_radial_values"]
        values = promoted["branch_values_over_Lambda"]
        lower = {
            key: Decimal(value["interval"]["lower_decimal"])
            for key, value in values.items()
        }
        self.assertGreater(lower["-4"], lower["-2"])
        self.assertGreater(lower["-2"], lower["2"])
        self.assertGreater(lower["2"], 0)
        self.assertFalse(promoted["identified_with_observed_particle_pole_masses"])

    def test_promoted_values_match_exact_reported_numbers(self) -> None:
        promoted = self.packet["promoted_radial_values"]
        expected = {
            "-4": Decimal("2.4685009745210706266233707476685"),
            "-2": Decimal("1.8948013019482695601737424133845"),
            "2": Decimal("0.7474019568026674272744857448165"),
        }
        for key, target in expected.items():
            interval = promoted["branch_values_over_Lambda"][key]["interval"]
            self.assertLess(Decimal(interval["lower_decimal"]), target)
            self.assertGreater(Decimal(interval["upper_decimal"]), target)
        h_interval = promoted["h_over_Lambda_interval"]
        h_target = Decimal("1.3211016293754684937241140791005")
        self.assertLess(Decimal(h_interval["lower_decimal"]), h_target)
        self.assertGreater(Decimal(h_interval["upper_decimal"]), h_target)

    def test_T28_operator_space_no_go_is_preserved(self) -> None:
        typed = self.packet["typed_no_go_reconciliation"]
        self.assertNotEqual(typed["CBF_T28_carrier"], typed["CBF_T34_carrier"])
        self.assertFalse(typed["generators_identified"])
        self.assertTrue(typed["T28_no_go_preserved"])
        self.assertFalse(typed["trace_substitution_across_carriers_used"])

    def test_no_fit_and_only_inherited_metrology_remain(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_observed_construction_inputs"], 0)
        self.assertEqual(ledger["new_fitted_coefficients"], 0)
        self.assertEqual(ledger["new_continuous_profile_parameters"], 0)
        self.assertEqual(ledger["new_sector_specific_scales"], 0)
        self.assertEqual(ledger["inherited_universal_metrology_primitives"], 1)
        self.assertFalse(ledger["absolute_dimensionful_scale_selected"])

    def test_physical_acceptance_boundary_is_not_overpromoted(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertTrue(boundary["same_root_direct_source_diagram_closed"])
        self.assertTrue(boundary["state_space_heat_profile_closed"])
        self.assertTrue(boundary["one_atom_measure_closed_at_declared_tier"])
        self.assertTrue(boundary["cutoff_unit_radial_values_closed_at_declared_tier"])
        self.assertFalse(boundary["full_upper_physical_source_closed"])
        self.assertFalse(boundary["full_four_dimensional_determinant_closed"])
        self.assertFalse(boundary["absolute_scale_closed"])
        self.assertFalse(boundary["nine_charged_Yukawa_values_closed"])
        self.assertFalse(boundary["held_out_observable_closed"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)

    def test_builder_check_ledger_is_green(self) -> None:
        summary = self.packet["check_summary"]
        self.assertEqual(summary["passed"], summary["total"])
        self.assertEqual(summary["failed"], [])
        self.assertTrue(all(self.packet["checks"].values()))


if __name__ == "__main__":
    unittest.main()
