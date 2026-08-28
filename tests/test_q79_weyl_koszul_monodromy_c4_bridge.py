"""Regression tests for the q79 Weyl-Koszul monodromy/C4 bridge."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = json.loads(
    (ROOT / "q79_weyl_koszul_monodromy_c4_cohomology_intertwiner.packet.json").read_text(
        encoding="utf-8"
    )
)


class Q79WeylKoszulMonodromyC4BridgeTests(unittest.TestCase):
    def test_exact_bridge_packet_passes(self) -> None:
        self.assertEqual(PACKET["summary"], {"all_passed": True, "passed": 46, "total": 46})

    def test_global_object_is_the_cohomology_shadow(self) -> None:
        self.assertTrue(PACKET["global_rootstack_cohomology_bridge"])
        self.assertFalse(PACKET["global_full_forward_difference_DGA"])

    def test_strain_intertwiner_recovers_selected_ranks(self) -> None:
        strain = PACKET["determinant_twisted_H1_strain_intertwiner"]
        self.assertEqual(strain["ranks"], {"invariant": 2, "TT": 4})

    def test_full_product_defects_are_executable(self) -> None:
        cutset = PACKET["product_and_globalization_cutset"]
        self.assertEqual(cutset["C4_full_DGA_defect_pairs_out_of_1296"], 108)
        self.assertEqual(cutset["S3_full_DGA_defect_pairs_out_of_1296"]["eps_-1_shift_0"], 360)

    def test_physical_hym_promotion_remains_open(self) -> None:
        self.assertFalse(PACKET["selected_nonzero_Chern_HYM_endpoint"])
        self.assertEqual(PACKET["continuous_fit_parameters"], 0)
        self.assertEqual(PACKET["observed_physical_inputs"], [])


if __name__ == "__main__":
    unittest.main()
