from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NormalFrameActionIntertwinerReductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(
            (ROOT / "normal_frame_action_intertwiner_reduction.packet.json").read_text(
                encoding="ascii"
            )
        )

    def test_selected_normal_object_is_a_line_not_a_frame(self) -> None:
        normal = self.packet["normal_line"]
        self.assertEqual(normal["carrier"], "N^c subset H16")
        self.assertEqual(normal["complex_dimension"], 1)
        self.assertEqual(normal["invariant_multiplicity"], 1)
        self.assertFalse(normal["unit_frame_selected"])

    def test_nonzero_normal_factorizations_are_one_GL1_orbit(self) -> None:
        quotient = self.packet["normal_frame_quotient"]
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(quotient["frame_group"], "GL(1,C)")
        self.assertEqual(quotient["invariant_contraction"], "H=epsilon o B")
        self.assertEqual(quotient["factorization_orbits_for_nonzero_H"], 1)
        self.assertFalse(quotient["separate_frame_is_physical_parameter"])
        self.assertEqual(ledger["normal_frame_parameters_after_quotient"], 0)

    def test_finite_family_trace_is_unique_but_not_physical_density(self) -> None:
        trace = self.packet["finite_trace"]
        self.assertEqual(trace["family_algebra"], "M3(C)")
        self.assertEqual(trace["Weyl_commutant_dimension"], 1)
        self.assertEqual(trace["response_AB_commutant_dimension"], 1)
        self.assertEqual(trace["functional"], "tau3(A)=Tr(A)/3")
        self.assertEqual(trace["finite_family_measure_parameters"], 0)
        self.assertFalse(trace["physical_BV_density_identified"])

    def test_contracted_response_norm_is_exact(self) -> None:
        response = self.packet["contracted_response"]
        self.assertEqual(
            (response["complex_dimension"], response["complex_rank"], response["complex_kernel"]),
            (48, 24, 24),
        )
        self.assertEqual(response["frobenius_norm_squared"], "192")
        self.assertEqual(response["normalized_full_trace_square"], "4")
        self.assertFalse(response["new_matrix_added"])

    def test_endpoint_exit_is_one_tensor_identity_and_coefficient(self) -> None:
        endpoint = self.packet["physical_intertwiner_minimal_data"]
        scale = self.packet["scale_nonidentifiability"]
        self.assertEqual(endpoint["required_identity"], "H_eff=c_action H_resp")
        self.assertEqual(
            endpoint["coefficient_formula"],
            "c_action=<H_resp,H_eff>_F/192",
        )
        self.assertTrue(endpoint["coefficient_is_unique_if_identity_holds"])
        self.assertFalse(endpoint["same_root_physical_intertwiner_supplied"])
        self.assertFalse(scale["normalized_shape_determines_absolute_scale"])

    def test_physical_and_value_boundaries_are_preserved(self) -> None:
        boundary = self.packet["claim_boundary"]
        ledger = self.packet["parameter_ledger"]
        self.assertFalse(boundary["physical_endpoint_selected"])
        self.assertFalse(boundary["physical_action_scale_selected"])
        self.assertFalse(boundary["Lorentz_Higgs_Yukawa_typing"])
        self.assertEqual(ledger["selected_physical_action_coefficients"], 0)
        self.assertEqual(ledger["strict_charged_magnitude_values_remaining"], 9)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
