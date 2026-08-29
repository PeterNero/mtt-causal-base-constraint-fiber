from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EquivariantFeshbachResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(
            (ROOT / "equivariant_feshbach_response.packet.json").read_text(
                encoding="ascii"
            )
        )

    def test_module_ladder_is_exact(self) -> None:
        ladder = self.packet["module_ladder"]
        self.assertEqual(ladder["dimension_chain"], [36, 18, 9, 1])
        self.assertEqual(ladder["gauge_sector_dimension"], 36)
        self.assertEqual(ladder["Fourier_paired_dimension"], 18)
        self.assertEqual(ladder["universal_routed_dimension"], 9)
        self.assertEqual(ladder["relative_response_line_dimension"], 1)

    def test_feshbach_covariance_does_not_select_the_line(self) -> None:
        feshbach = self.packet["feshbach_covariance"]
        self.assertTrue(feshbach["reducing_case_equivariant"])
        self.assertTrue(feshbach["nonreducing_case_equivariant"])
        self.assertFalse(feshbach["equivariance_alone_forces_response_line"])
        self.assertTrue(feshbach["negative_control"]["is_lane_Fourier_equivariant"])
        self.assertFalse(feshbach["negative_control"]["response_residual_zero"])

    def test_relative_intertwiner_is_one_dimensional(self) -> None:
        relative = self.packet["relative_intertwiner"]
        self.assertEqual(relative["comparison_commutant_dimension"], 1)
        self.assertEqual(
            relative["conclusion"], "H_eff,act=c_action H_resp,act"
        )
        self.assertFalse(relative["physically_supplied"])

    def test_exact_nonreducing_witness_recovers_scale(self) -> None:
        witness = self.packet["feshbach_covariance"]["exact_witness"]
        self.assertEqual(witness["retained_dimension"], 6)
        self.assertEqual(witness["complement_dimension"], 6)
        self.assertEqual(witness["target_scale"], "7/3")
        self.assertEqual(witness["recovered_scale"], "7/3")
        self.assertTrue(witness["residual_zero"])

    def test_endpoint_obligation_is_smaller_but_open(self) -> None:
        consequence = self.packet["endpoint_consequence"]
        boundary = self.packet["physical_boundary"]
        self.assertIn(
            "relative response algebra intertwiner",
            consequence["remaining_same_root_objects"],
        )
        self.assertFalse(boundary["physical_relative_response_intertwiner_supplied"])
        self.assertFalse(boundary["physical_action_scale_selected"])

    def test_no_physical_acceptance_or_hidden_fit(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["observed_construction_inputs"], 0)
        self.assertEqual(ledger["fitted_coefficients"], 0)
        self.assertEqual(ledger["new_physical_parameters"], 0)
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
