from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ClosurePressureFamilyHessianActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(
            (ROOT / "closure_pressure_family_hessian_activation.packet.json").read_text(
                encoding="utf-8"
            )
        )

    def test_regular_multiplier_requires_pressure_to_activate_curvature(self) -> None:
        theorem = self.packet["general_theorem"]
        self.assertEqual(
            theorem["pure_multiplier_critical_rule"],
            "surjectivity forces lambda=0",
        )
        self.assertIn("independent of D2psi", theorem["zero_pressure_Hessian"])
        self.assertEqual(
            theorem["tangent_Hessian"],
            "<u,H_p v>=p<n0,D2psi(0)[u,v]>",
        )

    def test_pressure_changes_the_exact_bordered_hessian(self) -> None:
        witness = self.packet["finite_instantiation"]
        self.assertEqual(witness["bordered_dimension_complex"], 80)
        self.assertEqual(witness["pure_multiplier_rank"], 32)
        self.assertEqual(witness["pure_multiplier_kernel_dimension"], 48)
        self.assertEqual(witness["pressured_bordered_rank"], 56)
        self.assertEqual(witness["pressured_bordered_kernel_dimension"], 24)

    def test_family_orientation_activates_without_three_magnitudes(self) -> None:
        symmetry = self.packet["symmetry_and_spectrum"]
        self.assertEqual(symmetry["free_family_stabilizer_before"], "U(3)")
        self.assertEqual(symmetry["common_family_stabilizer_after"], "U(1)")
        self.assertEqual(symmetry["joint_AB_commutant_dimension"], 1)
        self.assertTrue(symmetry["CP_sensitive_finite_orientation"])
        self.assertFalse(symmetry["three_distinct_positive_family_magnitudes"])

    def test_same_root_and_physical_action_remain_open(self) -> None:
        provenance = self.packet["source_provenance"]
        self.assertTrue(provenance["linear_source_pinned"])
        self.assertTrue(provenance["finite_response_source_pinned"])
        self.assertFalse(provenance["one_physical_root_for_both"])
        self.assertEqual(provenance["same_root_intertwiner_status"], "OPEN")
        self.assertTrue(all(value is False for value in self.packet["claim_boundary"].values()))

    def test_parameter_and_physical_boundaries_are_preserved(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["observed_construction_inputs"], 0)
        self.assertEqual(ledger["fitted_dimensionless_coefficients"], 0)
        self.assertEqual(ledger["unselected_physical_pressure_or_scale"], 1)
        self.assertEqual(ledger["strict_charged_magnitude_values_remaining"], 9)
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
