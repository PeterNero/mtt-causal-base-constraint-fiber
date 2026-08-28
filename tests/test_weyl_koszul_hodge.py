"""Regression tests for the selected finite Weyl-Koszul/Hodge theorem."""

from __future__ import annotations

import unittest

import build_selected_finite_weyl_koszul_hodge_and_interaction_cutset as construction


class WeylKoszulHodgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = construction.build_packet()

    def test_exact_twisted_dga_and_hodge_contraction(self) -> None:
        self.assertTrue(self.packet["summary"]["all_passed"])
        self.assertEqual(
            self.packet["hodge_contraction"]["cohomology"]["dimensions"],
            [1, 2, 1],
        )

    def test_spectator_lift_has_declared_harmonic_ranks(self) -> None:
        self.assertEqual(
            self.packet["hodge_contraction"]["cohomology"]["spectator_lift_ranks"],
            [96, 192, 96],
        )

    def test_higher_products_vanish_on_harmonic_center(self) -> None:
        transfer = self.packet["transferred_products"]
        self.assertEqual(transfer["m3_nonzero_basis_values"], 0)
        self.assertEqual(transfer["higher_products"], "m_n=0 for every n>=3")

    def test_equal_rank_96_spaces_are_transverse_not_equal(self) -> None:
        verdict = self.packet["completed_response_cutset"]["rank_96_verdict"]
        self.assertEqual(verdict["center_range_rank"], 96)
        self.assertEqual(verdict["D_fin_kernel_dimension"], 96)
        self.assertEqual(verdict["intersection_dimension"], 0)
        self.assertFalse(verdict["equal"])

    def test_physical_continuum_promotion_remains_open(self) -> None:
        self.assertTrue(self.packet["selected_finite_mtt_geometry"])
        self.assertFalse(self.packet["selected_continuum_mtt_physics"])
        self.assertEqual(self.packet["continuous_fit_parameters"], 0)


if __name__ == "__main__":
    unittest.main()
