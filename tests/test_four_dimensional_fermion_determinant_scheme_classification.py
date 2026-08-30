from __future__ import annotations

import json
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "four_dimensional_fermion_determinant_scheme_classification.packet.json"


class FourDimensionalFermionDeterminantSchemeClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_conditional_four_dimensional_shape_is_explicit(self) -> None:
        shape = self.packet["four_dimensional_shape"]
        self.assertEqual(shape["branch_factors"], {"-4": "1-2t", "-2": "1-t", "2": "1+t"})
        self.assertEqual(shape["chiral_multiplicity_each"], 16)
        self.assertEqual(shape["B_coefficients_ascending"], ["-2", "18", "-24", "18"])
        self.assertEqual(shape["Q4_coefficients_ascending"], ["3", "-8", "36", "-32", "18"])
        self.assertTrue(shape["conditional_pushforward_closed"])
        self.assertFalse(shape["selected_global_Lorentzian_determinant"])

    def test_scale_and_counterterm_orbit_prevent_unique_selection(self) -> None:
        orbit = self.packet["renormalization_orbit"]
        self.assertEqual(orbit["B_derivative_discriminant"], -1584)
        self.assertTrue(orbit["c1_can_set_slope_at_any_regular_point"])
        self.assertTrue(orbit["c2_can_set_curvature_after_slope_fix"])
        self.assertFalse(orbit["scheme_independent_stationary_coordinate"])
        self.assertFalse(orbit["selected_scalar_counterterm_rule"])

    def test_exact_interval_certificate_finds_two_roots(self) -> None:
        candidate = self.packet["MSbar_same_scale_candidate"]
        certificate = candidate["root_certificates"]
        self.assertEqual(certificate["exact_root_count_in_neutral_chamber"], 2)
        self.assertTrue(all(scan["ambiguous_cells"] == 0 for scan in candidate["outer_scans"]))
        self.assertEqual(candidate["stationary_points"]["local_maximum"]["type"], "local maximum")
        self.assertEqual(candidate["stationary_points"]["local_minimum"]["type"], "local minimum")

    def test_conventional_local_minimum_emits_reproducible_factors(self) -> None:
        minimum = self.packet["MSbar_same_scale_candidate"]["stationary_points"]["local_minimum"]
        self.assertAlmostEqual(float(minimum["decimal"]), 0.28128428279424317, places=15)
        self.assertGreater(Decimal(minimum["V_second_derivative"]), 0)
        factors = {key: Decimal(value) for key, value in minimum["branch_factors"].items()}
        self.assertGreater(factors["2"], factors["-2"])
        self.assertGreater(factors["-2"], factors["-4"])
        self.assertGreater(factors["-4"], 0)

    def test_candidate_is_metastable_not_global_or_selected(self) -> None:
        candidate = self.packet["MSbar_same_scale_candidate"]
        values = candidate["wall_and_stationary_values"]
        self.assertLess(Decimal(values["V_left_wall_limit"]), Decimal(values["V_local_minimum"]))
        self.assertFalse(candidate["global_minimum_in_open_neutral_chamber"])
        self.assertTrue(candidate["local_minimum_is_metastable"])
        self.assertTrue(candidate["conventional_candidate_only"])
        self.assertFalse(candidate["MTT_selected_physical_vacuum"])

    def test_T30_coordinate_requires_an_unselected_scale_choice(self) -> None:
        diagnostic = self.packet["T30_coordinate_scheme_diagnostic"]
        self.assertAlmostEqual(float(diagnostic["stationary_ell_decimal"]), -1.6789685371002474, places=15)
        self.assertAlmostEqual(float(diagnostic["MSbar_mu_over_h_decimal"]), 1.0936101291040974, places=15)
        self.assertFalse(diagnostic["independently_selected"])

    def test_source_coordinate_is_not_yet_a_dynamical_field(self) -> None:
        boundary = self.packet["dynamicality_and_global_boundary"]
        self.assertEqual(boundary["T25_role_of_t"], "coordinate in a finite Dirac-Yukawa source family")
        self.assertFalse(boundary["four_dimensional_kinetic_term_for_t_selected"])
        self.assertFalse(boundary["canonical_normalization_for_t_selected"])
        self.assertFalse(boundary["equation_of_motion_for_t_selected"])
        self.assertFalse(boundary["extremizing_profile_is_physical_equation_of_motion"])

    def test_no_observed_values_or_fit_enter_the_candidate(self) -> None:
        candidate = self.packet["MSbar_same_scale_candidate"]
        ledger = self.packet["parameter_ledger"]
        self.assertFalse(candidate["observed_values_used"])
        self.assertFalse(candidate["fitted_coefficients_used"])
        self.assertEqual(ledger["new_observed_construction_inputs"], 0)
        self.assertEqual(ledger["new_fitted_coefficients"], 0)
        self.assertEqual(ledger["candidate_convention_choice_count"], 4)
        self.assertEqual(ledger["candidate_choices_selected_by_MTT"], 0)
        self.assertEqual(ledger["accepted_new_physical_parameters"], 0)

    def test_physical_acceptance_boundary_stays_open(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertTrue(boundary["conditional_flat_4D_one_loop_shape_closed"])
        self.assertTrue(boundary["renormalization_scale_orbit_classified"])
        self.assertTrue(boundary["finite_local_counterterm_nonuniqueness_classified"])
        self.assertFalse(boundary["selected_four_dimensional_determinant_closed"])
        self.assertFalse(boundary["source_coordinate_dynamicality_closed"])
        self.assertFalse(boundary["renormalized_physical_vacuum_closed"])
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
