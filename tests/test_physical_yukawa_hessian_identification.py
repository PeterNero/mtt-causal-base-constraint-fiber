from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "physical_yukawa_hessian.packet.json"


class PhysicalYukawaHessianIdentificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_four_physical_channels_use_one_higgs(self) -> None:
        gauge = self.packet["one_higgs_gauge_covariance"]
        self.assertEqual(set(gauge["channels"]), {"u", "d", "e", "N"})
        self.assertEqual(gauge["selected_Higgs_representation"], "(1,2,+1/2)")
        self.assertTrue(all(value == 0 for value in gauge["hypercharge_6Y_sums"].values()))

    def test_incidence_is_physical_and_complementary(self) -> None:
        incidence = self.packet["carrier_and_incidence"]
        self.assertEqual(incidence["source_projector_rank"], 8)
        self.assertEqual(incidence["target_projector_rank"], 8)
        self.assertEqual(incidence["KO6_dimension"], 96)
        self.assertEqual(len(incidence["phase_pairs"]), 4)
        self.assertEqual(len(incidence["shift_pairs"]), 4)

    def test_physical_dirac_has_KO6_axioms(self) -> None:
        physical = self.packet["physical_dirac_family"]
        self.assertTrue(physical["self_adjoint"])
        self.assertTrue(physical["odd"])
        self.assertTrue(physical["J_real"])
        self.assertFalse(physical["auxiliary_T22_lift_relabelled_as_physical"])

    def test_T22_pair_is_exact_physical_hessian_compression(self) -> None:
        hessian = self.packet["hessian_compression"]
        self.assertEqual(hessian["target_rank"], 24)
        self.assertEqual(hessian["source_rank"], 24)
        self.assertEqual(hessian["particle_rank"], 48)
        self.assertEqual(hessian["KO6_rank"], 96)
        self.assertTrue(hessian["finite_physical_Yukawa_Laplacian_typed"])

    def test_radial_scale_is_not_a_new_knob(self) -> None:
        scale = self.packet["lorentzian_product_and_scale"]
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(scale["T22_coefficient_identification"], "mu^2=Lambda^2=h^2")
        self.assertFalse(scale["numerical_h_or_E0_selected"])
        self.assertEqual(ledger["new_observed_inputs"], 0)
        self.assertEqual(ledger["new_fitted_coefficients"], 0)
        self.assertEqual(ledger["sector_specific_scale_parameters"], 0)

    def test_selected_continuum_endpoint_is_not_overpromoted(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertTrue(boundary["finite_physical_Yukawa_Laplacian_typed"])
        self.assertFalse(boundary["full_selected_Lorentz_Higgs_Yukawa_endpoint"])
        self.assertFalse(boundary["upper_MTT_composite_root_selected"])
        self.assertFalse(boundary["numerical_Higgs_vacuum_selected"])
        self.assertFalse(boundary["continuum_HYM_intertwiner"])
        self.assertFalse(boundary["physical_BV4_pushforward"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
