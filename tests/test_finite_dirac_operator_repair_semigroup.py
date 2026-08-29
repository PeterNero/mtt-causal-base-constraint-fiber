from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "finite_dirac_operator_repair_semigroup.packet.json"


class FiniteDiracOperatorRepairSemigroupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_full_hessian_is_typed_and_exact(self) -> None:
        hessian = self.packet["hessian_superoperator"]
        self.assertEqual(hessian["exact_identity"], "A_rep=2(I+Ad_D0)=4P_comm")
        self.assertEqual(hessian["spectrum"], {"0": 4608, "4": 4608})
        self.assertEqual(hessian["rank"], 4608)
        self.assertEqual(hessian["nullity"], 4608)

    def test_tangent_normal_split_is_balanced(self) -> None:
        split = self.packet["tangent_normal_decomposition"]
        self.assertEqual(split["tangent_real_dimension"], 4608)
        self.assertEqual(split["normal_real_dimension"], 4608)
        self.assertTrue(split["finite_Morse_Bott"])

    def test_repair_semigroup_is_selected(self) -> None:
        semigroup = self.packet["repair_semigroup"]
        self.assertEqual(semigroup["exact_solution"], "T_s=P_anti+exp(-4s)P_comm")
        self.assertTrue(semigroup["contraction_for_nonnegative_s"])
        self.assertFalse(semigroup["physical_Lorentzian_time_identified"])

    def test_scalar_hessian_reconciles_with_operator_eigenvalue(self) -> None:
        pullback = self.packet["selected_family_pullback"]
        self.assertEqual(pullback["induced_metric_g_tt"], "2")
        self.assertEqual(pullback["scalar_Hessian"], "8")
        self.assertEqual(
            pullback["scalar_Hessian_interpretation"],
            "g_tt times normal eigenvalue 4",
        )
        self.assertEqual(pullback["linearized_scalar_rate"], "d_s t=-4t")

    def test_affine_family_is_not_full_nonlinear_flow_line(self) -> None:
        boundary = self.packet["nonlinear_flow_boundary"]
        self.assertEqual(boundary["decisive_difference"], "r_-2(t)-r_+2(t)=-6t^2")
        self.assertEqual(boundary["affine_family_invariant_only_at"], ["t=0"])
        self.assertTrue(boundary["scalar_flow_is_constrained_projection"])

    def test_repair_generator_is_not_material_R(self) -> None:
        comparison = self.packet["typed_operator_comparison"]
        self.assertEqual(comparison["A_rep_type"], "End_sa(H_F)->End_sa(H_F)")
        self.assertEqual(comparison["R_type"], "H_F->H_F")
        self.assertTrue(comparison["R_is_A_rep_eigenvector_not_A_rep"])
        self.assertFalse(comparison["repair_semigroup_equals_exp_minus_sR"])

    def test_repair_profile_closes_but_physical_profile_does_not(self) -> None:
        profile = self.packet["action_profile_boundary"]
        self.assertTrue(profile["same_root_exponential_repair_profile_selected"])
        self.assertFalse(profile["scalar_profile_f_of_D_phys_squared_selected"])
        self.assertFalse(profile["signed_cyclic_or_BV_action_selected"])

    def test_physical_acceptance_is_unchanged(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertTrue(boundary["full_operator_space_repair_Hessian_closed"])
        self.assertTrue(boundary["same_root_repair_semigroup_closed"])
        self.assertTrue(boundary["A84_general_mechanism_instantiated"])
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertFalse(boundary["B_SM_02_closed"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
