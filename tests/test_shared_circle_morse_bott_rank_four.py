from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "shared_circle_morse_bott_rank_four.packet.json"


class SharedCircleMorseBottRankFourTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_shared_circle_morse_bott_rank_four.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_builder_packet_passes(self) -> None:
        summary = self.packet["check_summary"]
        self.assertEqual(summary["failed"], [])
        self.assertEqual(summary["passed"], summary["total"])

    def test_projector_ranks_are_two_and_four(self) -> None:
        carrier = self.packet["q79_carrier"]
        self.assertEqual(carrier["rank_P"], 2)
        self.assertEqual(carrier["rank_Q"], 4)

    def test_shared_circle_is_only_zero_mode(self) -> None:
        vacuum = self.packet["shared_circle_vacuum"]
        self.assertTrue(vacuum["minimum_set_is_one_shared_circle_orbit"])
        self.assertTrue(vacuum["circle_tangent_is_only_Hessian_zero_mode"])
        self.assertEqual(vacuum["normal_rank"], 5)

    def test_equal_stiffness_fixes_alpha(self) -> None:
        action = self.packet["upper_action"]
        self.assertEqual(Fraction(action["unique_alpha"]), 4)
        self.assertEqual(action["uniqueness_equation"], "2 alpha=8")

    def test_rho_two_jet_vanishes(self) -> None:
        jets = [
            Fraction(value)
            for value in self.packet["determinant_lift"][
                "rho_jets_at_x1_through_order5"
            ]
        ]
        self.assertEqual(jets[:3], [0, 0, 0])
        self.assertEqual(jets[3:], [-16, -64, -48])

    def test_rank_four_profile_has_minimal_contact(self) -> None:
        coefficients = self.packet["determinant_lift"][
            "first_nonconstant_a_coefficients"
        ]
        self.assertEqual(Fraction(coefficients["(x-1)^3"]), Fraction(-4, 3))
        self.assertEqual(Fraction(coefficients["(x-1)^4"]), Fraction(-4, 3))
        self.assertEqual(Fraction(coefficients["(x-1)^5"]), Fraction(-1, 5))

    def test_full_remainder_is_emitted(self) -> None:
        determinant = self.packet["determinant_lift"]
        self.assertEqual(determinant["rank"], 4)
        self.assertTrue(determinant["full_T39_remainder_emitted"])
        self.assertEqual(
            determinant["half_log_determinant"],
            "(1/2)log det(K_Q(h)K_Q(H)^-1)=rho(h/H)",
        )

    def test_pointed_squares_close_in_model(self) -> None:
        pointed = self.packet["pointed_intertwiner"]
        self.assertTrue(pointed["fixed_point_square_closed_in_model"])
        self.assertTrue(pointed["tangent_generator_square_closed_in_model"])
        self.assertTrue(pointed["action_pushforward_closed_in_model"])

    def test_finite_and_physical_gates_are_distinguished(self) -> None:
        gates = self.packet["gate_ledger"]
        self.assertTrue(gates["G0_finite_determinant_equivalent_model"]["closed"])
        self.assertFalse(gates["G0_selected_physical_source"]["closed"])
        self.assertTrue(gates["G1_finite_Euclidean_tangent_isometry"]["closed"])
        self.assertFalse(gates["G1_physical_tangent_pairing"]["closed"])
        self.assertTrue(gates["G2_finite_normalized_Gaussian_BV_pushforward"]["closed"])
        self.assertFalse(gates["G2_selected_interacting_state_BV"]["closed"])

    def test_physical_counters_do_not_move(self) -> None:
        gates = self.packet["gate_ledger"]
        self.assertEqual((gates["physical_gluing_gates_closed"], gates["physical_gluing_gates_total"]), (0, 3))
        self.assertEqual((gates["physical_packets_accepted"], gates["physical_packets_total"]), (0, 3))
        self.assertEqual((gates["physical_rows_accepted"], gates["physical_rows_total"]), (0, 7))

    def test_no_new_fit_or_physical_parameter(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_fitted_parameters"], 0)
        self.assertEqual(ledger["new_observed_inputs"], 0)
        self.assertEqual(ledger["new_continuous_physical_parameters"], 0)

    def test_physical_guard_is_explicit(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertFalse(boundary["constructed_root_is_selected_upstream_root"])
        self.assertFalse(boundary["actual_physical_q79_normal_block_emitted"])
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertFalse(boundary["B_QFT_02_closed"])

    def test_independent_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_shared_circle_morse_bott_rank_four.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("independent checks:", result.stdout)


if __name__ == "__main__":
    unittest.main()
