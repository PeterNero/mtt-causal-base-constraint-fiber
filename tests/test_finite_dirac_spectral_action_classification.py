from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "finite_dirac_spectral_action_classification.packet.json"


class FiniteDiracSpectralActionClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_exact_factorization_is_emitted(self) -> None:
        factor = self.packet["exact_factorization"]
        self.assertEqual(factor["D1_identity"], "D1=(1/2)D0 H_phys")
        self.assertEqual(factor["D_identity"], "D_phys(t)=D0(I96+t H_phys/2)")
        self.assertEqual(factor["R_identity"], "R=D1^2=H_phys^2/4")
        self.assertTrue(factor["all_identities_exact"])

    def test_full_spectrum_has_three_equal_branches(self) -> None:
        spectrum = self.packet["full_spectrum"]
        self.assertEqual(
            spectrum["D_phys_squared"],
            {"(2t-1)^2": 32, "(t-1)^2": 32, "(t+1)^2": 32},
        )
        self.assertEqual(spectrum["singular_walls"], ["t=-1", "t=1/2", "t=1"])
        self.assertTrue(spectrum["phase_shift_lane_spectra_identical"])

    def test_universal_spectral_formula_is_complete(self) -> None:
        functional = self.packet["spectral_functional"]
        self.assertEqual(functional["normalized_trace"], "tau96=Tr/96")
        self.assertIn("f((2t-1)^2)", functional["exact_formula"])
        self.assertFalse(functional["profile_f_selected_by_trace_theorem"])

    def test_named_profiles_have_incompatible_stationary_points(self) -> None:
        profiles = self.packet["profile_examples"]
        self.assertEqual(profiles["dirac_norm"]["unique_global_minimizer"], "t=1/3")
        self.assertEqual(profiles["quartic_moment"]["stationary_equation"], "9t^3-12t^2+9t-1=0")
        self.assertEqual(profiles["defect_repair"]["unique_global_minimizer"], "t=0")
        self.assertEqual(profiles["normalized_logdet"]["stationary_equation"], "3t^2-t-1=0")

    def test_heat_family_has_no_common_stationary_coordinate(self) -> None:
        heat = self.packet["heat_profile_no_go"]
        self.assertTrue(heat["derivative_at_candidate_positive_for_all_tau"])
        self.assertFalse(heat["common_stationary_coordinate_exists"])
        self.assertFalse(heat["A53_tau_int_selects_profile_under_current_authority"])

    def test_closure_basepoint_is_not_zero_operator(self) -> None:
        coordinate = self.packet["coordinate_interpretation"]
        self.assertEqual(coordinate["closure_basepoint"], "t=0")
        self.assertFalse(coordinate["D_phys_at_closure_is_zero"])
        self.assertTrue(coordinate["D_phys_at_closure_is_unitary_involution"])
        self.assertFalse(coordinate["closure_basepoint_alone_emits_family_hierarchy"])

    def test_physical_action_and_values_remain_open(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertTrue(boundary["exact_full_finite_spectrum_closed"])
        self.assertTrue(boundary["profile_independent_value_selection_ruled_out"])
        self.assertFalse(boundary["selected_physical_action_profile"])
        self.assertFalse(boundary["strict_Yukawa_magnitudes_emitted"])
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertFalse(boundary["B_SM_02_closed"])


if __name__ == "__main__":
    unittest.main()
