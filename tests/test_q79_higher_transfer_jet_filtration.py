"""Regression tests for the all-arity higher-J cutset and m5 witness."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = json.loads(
    (ROOT / "q79_higher_transfer_jet_filtration_and_m5_feasibility.packet.json").read_text(
        encoding="utf-8"
    )
)


class HigherTransferJetFiltrationTests(unittest.TestCase):
    def test_packet_and_all_checks_pass(self) -> None:
        self.assertTrue(PACKET["all_checks_pass"])
        self.assertTrue(all(PACKET["checks"].values()))

    def test_all_eight_homotopy_images_have_the_certified_graded_dimension(self) -> None:
        records = PACKET["higher_jet_invariant_subspace_certificate"]["nonzero_modes"]
        self.assertEqual(len(records), 8)
        for record in records:
            self.assertEqual(record["invariant_span_dimension"], 6)
            self.assertEqual(record["homotopy_image_dimension"], 6)
            self.assertTrue(record["invariant_span_equals_homotopy_image"])
            self.assertEqual(record["degree_dimensions"], {"1": 2, "2": 3, "3": 1})
            self.assertEqual(record["closure_failures"], 0)
            self.assertEqual(record["terminal_projection_failures"], 0)

    def test_general_higher_J_cutset_is_proved(self) -> None:
        self.assertTrue(PACKET["general_n_minus_1_J_cutset_proved"])
        self.assertEqual(
            PACKET["higher_jet_invariant_subspace_certificate"]["pure_J_pair_homotopy_failures"],
            0,
        )

    def test_exact_m5_witness_is_nonzero(self) -> None:
        self.assertTrue(PACKET["transferred_m5_nonzero"])
        witness = PACKET["m5_selected_exact_probe"]["first_nonzero_m5_witness"]
        self.assertEqual(
            witness["inputs"],
            ["C:0,0,1", "C:0,0,1", "C:0,0,1", "C:1,0,1", "C:1,0,0"],
        )
        self.assertEqual(
            witness["output"],
            {"old": [[2, 0, 1, ["1/24", "1/48"]]], "higher_jet": []},
        )

    def test_selected_family_is_nonzero_at_every_arity(self) -> None:
        self.assertTrue(PACKET["transferred_mn_nonzero_for_every_n_ge_3_on_selected_family"])
        family = PACKET["selected_higher_arity_repeated_family_probe"]
        self.assertEqual(len(family["exact_records"]), 8)
        self.assertEqual(family["closed_form"]["conclusion"], "m_n is nonzero for every n>=3")

    def test_full_m5_and_physical_promotions_remain_open(self) -> None:
        self.assertFalse(PACKET["full_m5_table_computed"])
        self.assertFalse(PACKET["arity_five_Stasheff_identity_fully_verified"])
        self.assertFalse(PACKET["physical_D_fin_or_HYM_identification"])
        self.assertEqual(
            PACKET["m5_combinatorial_feasibility"]["remaining_after_proved_cheap_cutsets"],
            144_443_776,
        )


if __name__ == "__main__":
    unittest.main()
