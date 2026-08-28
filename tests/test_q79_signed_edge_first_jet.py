"""Regression tests for the signed-edge first-jet quotient theorem."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = json.loads(
    (ROOT / "q79_signed_edge_first_jet_harmonic_ideal_quotient.packet.json").read_text(
        encoding="utf-8"
    )
)


class SignedEdgeFirstJetTests(unittest.TestCase):
    def test_exact_packet_passes(self) -> None:
        self.assertEqual(PACKET["summary"], {"all_passed": True, "passed": 45, "total": 45})

    def test_principal_first_jet_is_the_canonical_odd_plane(self) -> None:
        self.assertTrue(PACKET["orientation_odd_plane_is_unique_principal_first_jet"])
        parity = PACKET["signed_edge_parity"]
        self.assertEqual(
            parity["odd_projector"],
            [["1", "0", "0", "0"], ["0", "1", "0", "0"], ["0", "0", "0", "0"], ["0", "0", "0", "0"]],
        )
        self.assertEqual(
            parity["Fourier_in_parity_basis"][:2],
            [["0", "-1", "0", "0"], ["1", "0", "0", "0"]],
        )

    def test_even_channel_starts_at_axial_second_order(self) -> None:
        split = PACKET["formal_first_second_jet_split"]
        self.assertEqual(split["principal_first_jet"], "nabla_x tensor o_x + nabla_z tensor o_z")
        self.assertEqual(
            split["first_even_term"],
            "h/2 (nabla_x^2 tensor e_x + nabla_z^2 tensor e_z)",
        )
        self.assertEqual(split["terms"][0]["even_coefficient"], "0")
        self.assertEqual(split["terms"][1]["even_coefficient"], "1/2")

    def test_all_extra_harmonics_are_one_exact_ideal(self) -> None:
        self.assertTrue(PACKET["twelve_extra_harmonic_classes_form_even_generated_ideal"])
        harmonic = PACKET["harmonic_ideal_quotient"]
        self.assertEqual(harmonic["even_generated_ideal"]["dimensions"], [0, 2, 5, 4, 1])
        self.assertEqual(harmonic["even_generated_ideal"]["total_dimension"], 12)
        self.assertEqual(harmonic["first_jet_quotient"]["dimensions"], [1, 2, 1, 0, 0])
        self.assertEqual(harmonic["first_jet_quotient"]["total_dimension"], 4)

    def test_hym_and_continuum_promotion_remain_open(self) -> None:
        self.assertTrue(PACKET["selected_harmonic_algebra_is_strict_quotient"])
        self.assertFalse(PACKET["selected_finite_to_continuum_intertwiner"])
        self.assertFalse(PACKET["selected_nonzero_Chern_HYM_endpoint"])
        self.assertFalse(PACKET["full_chain_associative_response_transfer"])
        self.assertFalse(PACKET["conditional_HYM_corollary"]["antecedent_selected_in_q79"])


if __name__ == "__main__":
    unittest.main()
