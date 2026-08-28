"""Regression tests for the symmetric q79 Weyl calculus theorem."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = json.loads(
    (ROOT / "q79_symmetric_weyl_calculus_isometric_retraction.packet.json").read_text(
        encoding="utf-8"
    )
)


class SymmetricWeylCalculusTests(unittest.TestCase):
    def test_exact_packet_passes(self) -> None:
        self.assertEqual(PACKET["summary"], {"all_passed": True, "passed": 52, "total": 52})

    def test_full_finite_covariance_is_exact(self) -> None:
        self.assertTrue(PACKET["symmetric_full_DGA_covariance"])
        group = PACKET["finite_covariance"]["generated_covariance_group"]
        self.assertEqual(group["order"], 36)
        self.assertFalse(group["physical_q79_structure_group_selected"])

    def test_half_edge_hodge_spectrum_and_cohomology(self) -> None:
        hodge = PACKET["normalized_Hodge_theory"]
        self.assertEqual(hodge["cohomology_dimensions"], [1, 4, 6, 4, 1])
        self.assertEqual(hodge["Green_eigenvalues"], ["1/3", "1/6"])

    def test_selected_complex_is_an_isometric_cochain_retract(self) -> None:
        self.assertTrue(PACKET["selected_old_complex_isometric_cochain_retract"])
        retract = PACKET["selected_complex_retract"]
        self.assertEqual(retract["selected_harmonic_dimensions"], [1, 2, 1, 0, 0])
        self.assertEqual(retract["extra_harmonic_dimensions"], [0, 2, 5, 4, 1])

    def test_product_and_physical_boundaries_remain_open(self) -> None:
        self.assertFalse(PACKET["selected_old_complex_full_product_retract"])
        diagnostics = PACKET["selected_complex_retract"]["product_diagnostics"]
        self.assertEqual(diagnostics["compressed_vs_old_defect_pairs"], 504)
        self.assertEqual(diagnostics["nonzero_associator_triples"], 4464)
        self.assertFalse(PACKET["symmetric_extra_harmonic_modes_selected_physical"])
        self.assertFalse(PACKET["selected_nonzero_Chern_HYM_endpoint"])


if __name__ == "__main__":
    unittest.main()
