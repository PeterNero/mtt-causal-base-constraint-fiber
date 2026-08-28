"""Regression tests for the symmetric-response transfer theorem."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = json.loads(
    (ROOT / "q79_symmetric_response_retraction_transferred_m3.packet.json").read_text(
        encoding="utf-8"
    )
)


class SymmetricResponseTransferTests(unittest.TestCase):
    def test_exact_packet_passes(self) -> None:
        self.assertEqual(PACKET["summary"], {"all_passed": True, "passed": 33, "total": 33})

    def test_48_dimensional_strong_deformation_retract(self) -> None:
        self.assertTrue(PACKET["strong_deformation_retract_to_old_plus_higher_jet_ideal"])
        target = PACKET["strong_deformation_retract"]["target"]
        self.assertEqual(target["degree_dimensions"], [9, 20, 14, 4, 1])
        self.assertEqual(target["total_dimension"], 48)
        self.assertEqual(target["cohomology_dimensions"], [1, 4, 6, 4, 1])

    def test_transferred_m2_and_m3_are_fully_executed_at_declared_arity(self) -> None:
        transfer = PACKET["transferred_structure"]
        self.assertEqual(transfer["m2"]["nonzero_basis_pairs"], 881)
        self.assertEqual(transfer["m2_associativity"]["nonzero_target_associators"], 7124)
        self.assertEqual(transfer["m3"]["nonzero_basis_triples"], 17204)
        self.assertEqual(transfer["m3"]["nonzero_associator_and_m3_basis_triples"], 3580)
        self.assertEqual(len(transfer["m2"]["nonzero_table_sha256"]), 64)
        self.assertEqual(len(transfer["m3"]["nonzero_table_sha256"]), 64)

    def test_m3_support_respects_harmonic_and_higher_jet_boundaries(self) -> None:
        ternary = PACKET["transferred_structure"]["m3"]
        self.assertEqual(ternary["harmonic_input_nonzero_basis_triples"], 0)
        self.assertEqual(ternary["two_or_more_higher_jet_input_nonzero_basis_triples"], 0)
        self.assertEqual(ternary["old_input_nonzero_basis_triples"], 11540)
        self.assertNotIn("JJJ->jet", ternary["sector_counts"])

    def test_higher_arity_and_physical_promotion_remain_open(self) -> None:
        self.assertTrue(PACKET["transferred_m3_computed"])
        self.assertFalse(PACKET["transferred_m4_and_higher_computed"])
        self.assertFalse(PACKET["target_identified_with_D_fin"])
        self.assertFalse(PACKET["selected_nonzero_Chern_HYM_endpoint"])
        self.assertFalse(PACKET["physical_action_selected"])


if __name__ == "__main__":
    unittest.main()
