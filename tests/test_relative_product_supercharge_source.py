from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RelativeProductSuperchargeSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(
            (ROOT / "relative_product_supercharge.packet.json").read_text(
                encoding="ascii"
            )
        )

    def test_finite_response_is_one_supercharge_square_derivative(self) -> None:
        routed = self.packet["routed_internal_family"]
        odd = self.packet["odd_supercharge"]
        self.assertEqual(routed["target_rank"], 24)
        self.assertEqual(routed["target_norm_squared"], "192")
        self.assertEqual(
            odd["derivative"],
            "D_F(t)^2|_0'=diag(H_+,H_-)",
        )
        self.assertTrue(odd["minimal_odd_self_adjoint_lift_unique"])

    def test_causal_and_finite_parts_share_one_operator_family(self) -> None:
        product = self.packet["relative_product_operator"]
        provenance = self.packet["root_provenance"]
        self.assertTrue(product["full_response_and_causal_part_from_one_operator_family"])
        self.assertTrue(provenance["deterministic_composite_root"])
        self.assertTrue(provenance["single_operator_family_proved"])
        self.assertTrue(provenance["target_response_excluded"])

    def test_t21_coefficient_is_one_universal_scale_squared(self) -> None:
        product = self.packet["relative_product_operator"]
        scale = self.packet["causal_and_scale"]
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(product["T21_identification"], "mu^2=Lambda^2")
        self.assertEqual(scale["one_anchor_identification"], "Lambda=E0=1/L0")
        self.assertEqual(ledger["universal_dimensionful_primitives"], 1)
        self.assertEqual(ledger["sector_specific_scale_parameters"], 0)

    def test_relative_shape_is_scale_free_but_absolute_value_is_not(self) -> None:
        scale = self.packet["causal_and_scale"]
        ledger = self.packet["parameter_ledger"]
        self.assertTrue(scale["dimensionless_response_line_scale_invariant"])
        self.assertTrue(scale["absolute_scale_no_go"])
        self.assertFalse(scale["numerical_E0_or_L0_selected"])
        self.assertEqual(ledger["relative_prediction_parameters"], 0)

    def test_auxiliary_doubling_is_not_particle_doubling(self) -> None:
        odd = self.packet["odd_supercharge"]
        self.assertEqual(odd["dimension"], 96)
        self.assertTrue(odd["auxiliary_not_physical_particle_doubling"])

    def test_physical_endpoint_is_not_overpromoted(self) -> None:
        provenance = self.packet["root_provenance"]
        boundary = self.packet["physical_boundary"]
        self.assertFalse(provenance["upper_MTT_selection_proved"])
        self.assertFalse(provenance["same_physical_root_proved"])
        self.assertFalse(boundary["Lorentz_Higgs_Yukawa_identification"])
        self.assertFalse(boundary["continuum_HYM_intertwiner"])
        self.assertFalse(boundary["physical_BV4_pushforward"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
