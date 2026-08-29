from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "direct_dirac_defect_repair_action.packet.json"


class DirectDiracDefectRepairActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_exact_affine_defect_is_emitted(self) -> None:
        defect = self.packet["defect_residual"]
        self.assertEqual(defect["exact_expansion"], "K(t)=t H_phys+t^2 R")
        self.assertEqual(defect["H_phys_rank"], 96)
        self.assertEqual(defect["R_rank"], 96)
        self.assertTrue(defect["H_phys_self_adjoint"])
        self.assertTrue(defect["R_self_adjoint"])
        self.assertTrue(defect["H_phys_R_commute"])

    def test_complete_repair_polynomial_is_exact(self) -> None:
        action = self.packet["normalized_repair_action"]
        coefficients = self.packet["exact_coefficients"]
        self.assertEqual(action["exact_polynomial"], "4 t^2-(16/3)t^3+3t^4")
        self.assertEqual(coefficients["coefficient_t2"], "4")
        self.assertEqual(coefficients["coefficient_t3"], "-16/3")
        self.assertEqual(coefficients["coefficient_t4"], "3")
        self.assertEqual(coefficients["Hessian_at_zero"], "8")

    def test_repair_action_has_only_the_closure_stationary_point(self) -> None:
        positivity = self.packet["positivity_and_stationarity"]
        self.assertTrue(positivity["nonnegative_for_all_real_t"])
        self.assertEqual(positivity["zero_set"], ["t=0"])
        self.assertEqual(positivity["real_stationary_set"], ["t=0"])
        self.assertEqual(positivity["global_minimizer"], "t=0")
        self.assertFalse(positivity["nonzero_value_selected"])

    def test_uniqueness_is_scoped_to_the_quadratic_defect_class(self) -> None:
        uniqueness = self.packet["uniqueness_scope"]
        self.assertEqual(uniqueness["unique_trace"], "Tr/96")
        self.assertTrue(uniqueness["unique_up_to_positive_scale"])
        self.assertEqual(uniqueness["standard_gradient_normalization"], "c=1/2")
        self.assertFalse(uniqueness["physical_absolute_scale_selected"])

    def test_continuum_lift_has_h_fourth_scaling_only(self) -> None:
        continuum = self.packet["continuum_lift"]
        self.assertEqual(continuum["relative_defect"], "K_dir,rel(t,h)=h^2 I tensor K(t)")
        self.assertEqual(continuum["normalized_local_repair_density"], "S_dir,rep(t,h)=h^4 S_rep(t)")
        self.assertFalse(continuum["principal_symbol_changed"])
        self.assertFalse(continuum["spacetime_integrated_physical_action_claimed"])
        self.assertFalse(continuum["numerical_h_selected"])

    def test_positive_repair_is_not_relabelled_as_signed_action(self) -> None:
        boundary = self.packet["action_boundary"]
        self.assertTrue(boundary["H4_T9_obeyed"])
        self.assertFalse(boundary["H4_T10_cyclic_action_replaced"])
        self.assertTrue(boundary["positive_repair_is_not_signed_action"])
        self.assertFalse(boundary["Lorentzian_density_selected"])
        self.assertFalse(boundary["BV_QME_selected"])

    def test_physical_acceptance_and_blockers_do_not_move(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertTrue(boundary["exact_finite_repair_action_closed"])
        self.assertTrue(boundary["full_quartic_repair_jet_closed"])
        self.assertFalse(boundary["internal_coefficients_are_physical_observables"])
        self.assertFalse(boundary["signed_physical_action_selected"])
        self.assertFalse(boundary["held_out_physical_observable_emitted"])
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertFalse(boundary["B_SM_02_closed"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
