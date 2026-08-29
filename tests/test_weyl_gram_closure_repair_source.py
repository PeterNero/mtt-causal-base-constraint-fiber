from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WeylGramClosureRepairSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(
            (ROOT / "weyl_gram_closure_repair_source.packet.json").read_text(
                encoding="ascii"
            )
        )

    def test_primitive_root_does_not_contain_target_response(self) -> None:
        primitive = self.packet["primitive_source"]
        self.assertEqual(primitive["operators"], ["P", "X", "Z", "F3"])
        self.assertTrue(primitive["target_response_excluded_from_root"])
        self.assertNotIn("H_resp", primitive["primitive_payload"])
        self.assertNotIn("A_shift", primitive["primitive_payload"])
        self.assertNotIn("B_phase", primitive["primitive_payload"])

    def test_response_blocks_are_exact_Gram_variations(self) -> None:
        derivation = self.packet["gram_derivation"]
        self.assertTrue(derivation["first_variations_derived"])
        self.assertEqual(
            derivation["exact_derivative_formula"],
            "G_M'(0)=-(P M^*+M P)",
        )
        self.assertTrue(derivation["Fourier_covariant_for_all_t"])

    def test_source_coordinate_reduction_is_four_to_two_to_one(self) -> None:
        routing = self.packet["universal_routing"]
        self.assertEqual(routing["coordinate_dimension_ladder"], [4, 2, 1])
        self.assertEqual(routing["shared_coordinate"], ["t", "t", "t", "t"])
        self.assertTrue(routing["shared_coordinate_forced"])

    def test_relative_response_intertwiner_is_closed_finitely(self) -> None:
        relative = self.packet["relative_intertwiner"]
        self.assertEqual(relative["active_response_rank"], 6)
        self.assertTrue(relative["T_rel_is_identity"])
        self.assertTrue(relative["commutators_zero"])
        self.assertTrue(relative["finite_source_line_derived"])
        self.assertEqual(relative["normalized_finite_coefficient"], "1")

    def test_affine_action_is_compatible_but_not_physical_SYN(self) -> None:
        finite_action = self.packet["finite_action"]
        self.assertTrue(finite_action["finite_identity_synthesis"])
        self.assertGreater(finite_action["graph_pullback_samples"], 0)
        self.assertFalse(finite_action["physical_SYN_packet"])

    def test_no_hidden_fit_or_physical_promotion(self) -> None:
        ledger = self.packet["parameter_ledger"]
        boundary = self.packet["physical_boundary"]
        self.assertEqual(ledger["observed_construction_inputs"], 0)
        self.assertEqual(ledger["fitted_matrix_coefficients"], 0)
        self.assertEqual(ledger["new_continuous_response_shape_parameters"], 0)
        self.assertEqual(ledger["shared_finite_source_coordinates"], 1)
        self.assertFalse(boundary["physically_selected"])
        self.assertFalse(boundary["eta9_or_HYM_endpoint_used"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()

